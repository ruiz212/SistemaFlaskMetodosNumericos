import numpy as np

def _evaluar_1d(f, a, b, n):
    """Evalúa la función f en n puntos equiespaciados en [a,b]."""
    x = np.linspace(a, b, n)
    try:
        y = f(x)
        if np.isscalar(y):
            y = np.full_like(x, y)
        return x, y
    except Exception:
        # Fallback si f no vectoriza bien
        y = np.array([f(xi) for xi in x])
        return x, y

def trapecio(a, b, n, f, is_double=False):
    """Regla del trapecio (simple y compuesta)."""
    if n < 1:
        return {"error": "El número de intervalos n debe ser mayor o igual a 1."}
        
    x, y = _evaluar_1d(f, a, b, n + 1)
    h = (b - a) / n
    
    if n == 1:
        integral = (h / 2) * (y[0] + y[1])
        pasos = [
            f"h = ({b} - {a}) / 1 = {h}",
            f"I = (h / 2) * (f(x0) + f(x1))",
            f"I = ({h} / 2) * ({y[0]:.6g} + {y[1]:.6g}) = {integral:.6g}"
        ]
    else:
        suma_interna = np.sum(y[1:-1])
        integral = (h / 2) * (y[0] + 2 * suma_interna + y[-1])
        pasos = [
            f"h = ({b} - {a}) / {n} = {h}",
            f"I = (h / 2) * (f(x0) + 2*Σf(xi) + f(xn))",
            f"I = ({h} / 2) * ({y[0]:.6g} + 2*({suma_interna:.6g}) + {y[-1]:.6g}) = {integral:.6g}"
        ]
        
    return {
        "integral": integral,
        "pasos": pasos,
        "x": x.tolist() if not is_double else [],
        "y": y.tolist() if not is_double else []
    }

def romberg(a, b, niveles, f, is_double=False):
    """Integración de Romberg."""
    if niveles < 1:
        return {"error": "El número de niveles debe ser mayor o igual a 1."}
        
    R = np.zeros((niveles, niveles))
    pasos = []
    
    pasos.append(f"Cálculo de la primera columna (k=1) mediante Trapecio:")
    for j in range(niveles):
        n_trap = 2**(j+1)
        h = (b - a) / n_trap
        
        x, y = _evaluar_1d(f, a, b, n_trap + 1)
        
        if n_trap == 1:
            integral_trap = (h / 2) * (y[0] + y[1])
        else:
            suma_interna = np.sum(y[1:-1])
            integral_trap = (h / 2) * (y[0] + 2 * suma_interna + y[-1])
            
        R[j, 0] = integral_trap
        pasos.append(f"j={j+1}, n={n_trap}, h={h}: I_{j+1,1} = {integral_trap:.8f}")

    for k in range(1, niveles):
        pasos.append(f"\nCálculo de la columna k={k+1}:")
        factor = 4**k
        for j in range(niveles - k):
            R[j, k] = (factor * R[j+1, k-1] - R[j, k-1]) / (factor - 1)
            pasos.append(f"j={j+1}: I_{j+1,{k+1}} = ( {factor} * {R[j+1, k-1]:.8f} - {R[j, k-1]:.8f} ) / {factor - 1} = {R[j, k]:.8f}")
            
    integral = R[0, niveles-1]
    
    pasos.append(f"\nMatriz de Romberg:")
    for j in range(niveles):
        fila = []
        for k in range(niveles):
            if k <= niveles - 1 - j:
                fila.append(f"{R[j, k]:.8f}")
            else:
                fila.append("0.00000000")
        pasos.append("   ".join(fila))
        
    return {
        "integral": integral,
        "pasos": pasos,
        "x": [],
        "y": []
    }

def integrar(metodo, a, b, n, f, is_double=False):
    if metodo == "Trapecio":
        return trapecio(a, b, n, f, is_double)
    elif metodo == "Romberg":
        return romberg(a, b, n, f, is_double)
    else:
        return {"error": "Método no soportado."}

def integrar_doble(metodo, ax, bx, nx, ay, by, ny, f):
    """
    Integral doble sobre región rectangular [ax,bx] x [ay,by].
    Integramos primero respecto a y, y luego respecto a x.
    I = ∫_ax^bx [ ∫_ay^by f(x,y) dy ] dx
    """
    # Función que evalúa la integral interna respecto a y, para un x fijo
    def integral_interna(x_val):
        # Creamos una función g(y) = f(x_val, y)
        def g(y_val):
            # Try to vectorize
            if isinstance(y_val, np.ndarray):
                return np.array([f(x_val, yi) for yi in y_val])
            return f(x_val, y_val)
            
        res = integrar(metodo, ay, by, ny, g, is_double=True)
        if "error" in res:
            raise ValueError(res["error"])
        return res["integral"]

    try:
        # Ahora integramos integral_interna(x) respecto a x
        # Envolvemos integral_interna para que acepte arrays de numpy
        def f_exterior(x_val):
            if isinstance(x_val, np.ndarray):
                return np.array([integral_interna(xi) for xi in x_val])
            return integral_interna(x_val)

        res_final = integrar(metodo, ax, bx, nx, f_exterior, is_double=True)
        
        if "error" in res_final:
            return {"error": res_final["error"]}
            
        res_final["pasos"] = [
            f"Integrando la función doble con {metodo}.",
            f"Límites X: [{ax}, {bx}], particiones nx = {nx}",
            f"Límites Y: [{ay}, {by}], particiones ny = {ny}",
            "Se evalúa primero la integral interna ∫ f(x,y) dy para cada nodo x,",
            "luego se integra el resultado respecto a x."
        ] + res_final["pasos"]
        
        return res_final
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Error evaluando integral doble: {str(e)}"}
