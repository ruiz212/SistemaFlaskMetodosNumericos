import sympy as sp
import numpy as np
from metodos.utils import parse_ecuacion

def resolver_sistema_no_lineal(n, funciones_txt, valores_x, tol, max_iter, modo_angulo='rad'):
    """
    Resuelve un sistema de n ecuaciones no lineales usando el método de Newton-Raphson.
    Optimizado para usar lambdify con matrices de SymPy para mayor velocidad.
    """
    try:
        X = np.array([float(x) for x in valores_x], dtype=float)
    except (ValueError, TypeError):
        return {"error": "Los valores iniciales deben ser numéricos."}
    
    F_sym = []
    for i, eq_text in enumerate(funciones_txt):
        if not eq_text: return {"error": f"Ecuación f_{i+1} vacía."}
        try:
            expr = parse_ecuacion(eq_text, modo_angulo)
            F_sym.append(expr)
        except Exception as e:
            return {"error": f"Sintaxis inválida en f_{i+1}:\n{str(e)}"}
            
    simbolos_usados = set()
    for expr in F_sym:
        if hasattr(expr, 'free_symbols'):
            simbolos_usados.update(expr.free_symbols)
            
    # Ordenar símbolos alfabéticamente (x, y, z...) para consistencia con el vector de entrada
    simbolos = sorted(list(simbolos_usados), key=lambda s: s.name)
    
    # Validar que no haya más símbolos que ecuaciones
    if len(simbolos) > n:
        nombres = ', '.join([s.name for s in simbolos])
        return {"error": f"Se detectaron {len(simbolos)} variables ({nombres}) pero solo hay {n} ecuaciones."}
        
    # Si hay menos símbolos, rellenar con nombres genéricos para completar n
    while len(simbolos) < n:
        simbolos.append(sp.Symbol(f"var_extra_{len(simbolos)}"))
        
    consola = []
    consola.append("=== SISTEMA NO LINEAL (NEWTON-RAPHSON) ===")
    consola.append(f"Variables detectadas: {', '.join([s.name for s in simbolos])}")
    consola.append(f"Tolerancia: {tol}, Max Iter: {max_iter}\n")
    
    # --- PREPARACIÓN MATRICIAL (OPTIMIZADO PARA VELOCIDAD) ---
    print(f"[DEBUG] Iniciando preparación de funciones para n={n}")
    
    # Calcular Jacobiana simbólica
    print("[DEBUG] Calculando Jacobiana simbólica...")
    F_mat = sp.Matrix(F_sym)
    J_mat = F_mat.jacobian(simbolos)
    
    # Lambdificar individualmente (mucho más rápido que lambdificar la matriz completa)
    # Usamos 'math' para máxima velocidad en cálculos escalares
    print("[DEBUG] Compilando funciones f_i...")
    f_funcs = [sp.lambdify(simbolos, f, modules=['math', 'numpy']) for f in F_sym]
    
    print("[DEBUG] Compilando Jacobiana J_ij...")
    j_funcs = []
    for r in range(n):
        fila_funcs = []
        for c in range(n):
            fila_funcs.append(sp.lambdify(simbolos, J_mat[r, c], modules=['math', 'numpy']))
        j_funcs.append(fila_funcs)
    
    print("[DEBUG] Compilación terminada.")

    headers = ["Iteración"] + [f"{s.name}" for s in simbolos] + ["Error Máx"]
    resultados = []
    
    error = float('inf')
    iteracion = 0

    print("[DEBUG] Iniciando bucle de iteraciones...")
    while error > tol and iteracion < max_iter:
        print(f"[DEBUG] Iteración {iteracion} - Punto: {X}")
        try:
            # Evaluar vector F y matriz J elemento a elemento
            # Esto evita el overhead de Matrix/Array de SymPy en el bucle
            F_eval = np.array([f(*X) for f in f_funcs], dtype=float)
            
            J_eval = np.zeros((n, n))
            for r in range(n):
                for c in range(n):
                    J_eval[r, c] = j_funcs[r][c](*X)
            
        except Exception as e:
            print(f"[DEBUG] Error en evaluación: {e}")
            consola.append(f"Error de evaluación en iteración {iteracion}: {e}")
            return {"error": f"Error matemático: {str(e)}", "consola": consola}

        # Registrar estado actual antes del paso
        error_display = f"{error:.8f}" if iteracion > 0 else "---"
        fila_data = [str(iteracion)] + [f"{val:.8f}" for val in X] + [error_display]
        resultados.append(fila_data)

        # Paso de Newton: X_nuevo = X - J^-1 * F
        try:
            # Resolver el sistema lineal J * delta = F es más estable que invertir J
            delta_X = np.linalg.solve(J_eval, F_eval)
        except np.linalg.LinAlgError:
            consola.append(f"Matriz Jacobiana singular en iteración {iteracion}. No se puede invertir.")
            return {"error": "El sistema es singular (determinante cero). Prueba con otros valores iniciales.", "consola": consola}

        X_nuevo = X - delta_X
        
        # Calcular error como la norma infinita de la diferencia
        error = np.max(np.abs(delta_X))
        
        X = X_nuevo
        iteracion += 1

    # Agregar última fila de resultados
    error_final = f"{error:.8f}"
    fila_final = [str(iteracion)] + [f"{val:.8f}" for val in X] + [error_final]
    resultados.append(fila_final)

    if error <= tol:
        consola.append(f"\nConvergió exitosamente en {iteracion} iteraciones.")
        consola.append(f"Error final: {error:.8f}")
    else:
        consola.append(f"\nNo se alcanzó la tolerancia en {max_iter} iteraciones.")
        consola.append("El sistema podría estar divergiendo o requiere más iteraciones.")

    return {
        "resultados": resultados, 
        "headers": headers, 
        "consola": consola, 
        "raiz": X.tolist(),
        "var_names": [s.name for s in simbolos]
    }
