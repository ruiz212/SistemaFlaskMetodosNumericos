def secante(x0, x1, tol, f):
    resultados = []
    c_prev, c_actual, iteracion = x0, x1, 0
    raiz_encontrada = None
    while True:
        f_prev, f_actual = f(c_prev), f(c_actual)
        if (f_actual - f_prev) == 0: return {"error": "Error: División por cero."}
        c_nuevo = c_actual - (f_actual * (c_actual - c_prev)) / (f_actual - f_prev)
        f_nuevo = f(c_nuevo)
        
        error_rp = abs((c_nuevo - c_actual) / c_nuevo) * 100.0 if (iteracion > 0 and c_nuevo != 0) else 100.0
        error_str = f"{error_rp:.4f}%" if iteracion > 0 else "---"
        
        resultados.append({
            'iter': iteracion, 'ci': f"{c_nuevo:.7f}", 'fci': f"{f_nuevo:.7f}", 'error': error_str
        })
        
        if (iteracion > 0 and error_rp < tol) or f_nuevo == 0:
            raiz_encontrada = c_nuevo
            break
        c_prev, c_actual, iteracion = c_actual, c_nuevo, iteracion + 1
        if iteracion > 200: return {"error": "Error: divergencia."}
    return {"resultados": resultados, "raiz": raiz_encontrada, "mensaje": f"Secante | Raíz: {raiz_encontrada:.8f}"}
