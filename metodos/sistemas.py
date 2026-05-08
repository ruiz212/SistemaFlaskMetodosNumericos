import sympy as sp
import numpy as np
from metodos.utils import parse_ecuacion

def resolver_sistema_no_lineal(n, funciones_txt, valores_x, tol, max_iter, modo_angulo='rad'):
    X0 = np.array([float(x) for x in valores_x])
    
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
            
    simbolos = sorted(list(simbolos_usados), key=lambda s: s.name)
    if len(simbolos) > n:
        return {"error": f"Se detectaron {len(simbolos)} variables ({', '.join([s.name for s in simbolos])}) pero solo hay {n} ecuaciones."}
        
    while len(simbolos) < n:
        simbolos.append(sp.Symbol(f"var_extra_{len(simbolos)}"))
        
    consola = []
    consola.append("=== GENERANDO JACOBIANO ===")
    consola.append(f"Variables ordenadas: {', '.join([s.name for s in simbolos])}\n")
    
    J_sym = []
    for f in F_sym:
        fila_J = [sp.diff(f, sim) for sim in simbolos]
        J_sym.append(fila_J)

    F_func = [sp.lambdify(simbolos, f, 'numpy') for f in F_sym]
    J_func = [[sp.lambdify(simbolos, j, 'numpy') for j in fila] for fila in J_sym]

    headers = ["Iteración"] + [f"{s.name}" for s in simbolos] + ["Error"]
    
    iteracion = 0
    error = float('inf')
    X = X0.copy()

    def evaluar_F(X_val):
        return np.array([float(f(*X_val)) if not isinstance(f(*X_val), np.ndarray) else float(f(*X_val)[0]) for f in F_func])
        
    def evaluar_J(X_val):
        mat = np.zeros((n, n))
        for r in range(n):
            for c in range(n):
                val = J_func[r][c](*X_val)
                mat[r, c] = float(val) if np.isscalar(val) else float(np.array(val).flatten()[0])
        return mat

    resultados = []
    
    while error > tol and iteracion <= max_iter:
        try:
            F_val = evaluar_F(X)
            J_val = evaluar_J(X)
        except Exception as e:
            consola.append(f"Error evaluando funciones en iteración {iteracion}: {e}")
            return {"error": f"Error de evaluación: {str(e)}", "consola": consola}

        consola.append(f"\\n--- Iteración {iteracion} ---")
        consola.append("Jacobiana:")
        for row in J_val:
            consola.append("  [ " + "  ".join([f"{val:9.4f}" for val in row]) + " ]")

        try:
            J_inv = np.linalg.inv(J_val)
        except np.linalg.LinAlgError:
            consola.append(f"Matriz singular en iteración {iteracion}.")
            return {"error": "El sistema es singular con los valores actuales. La matriz Jacobiana no se puede invertir.", "consola": consola}

        delta_X = J_inv @ F_val
        X_nuevo = X - delta_X
        
        error = np.max(np.abs(X_nuevo - X))
        
        fila_data = [str(iteracion)] + [f"{x:.6f}" for x in X] + [f"{error:.6f}" if iteracion > 0 else "-"]
        resultados.append(fila_data)
        
        X = X_nuevo
        iteracion += 1

    if error <= tol:
        fila_data = [str(iteracion)] + [f"{x:.6f}" for x in X] + [f"{error:.6f}"]
        resultados.append(fila_data)
        
        consola.append(f"Convergió en {iteracion} iteraciones.")
        consola.append("=== SOLUCIÓN ===")
        for i, x in enumerate(X):
            consola.append(f"x_{i+1} = {x:.6f}")
    else:
        consola.append(f"No convergió en el máximo de iteraciones ({max_iter}).")
        
    return {"resultados": resultados, "headers": headers, "consola": consola}
