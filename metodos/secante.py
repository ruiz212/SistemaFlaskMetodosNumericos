def secante(x0, x1, tol, f):
    resultados = []
    raiz_encontrada = None

    # Evaluar los puntos iniciales
    f0 = f(x0)
    f1 = f(x1)
    if f0 is None or f1 is None:
        return {"error": "Error evaluando la función en los puntos iniciales."}

    # Mostrar la iteración 1 (primer cálculo usando x0 y x1)
    iteracion = 1
    c_prev   = x0
    c_actual = x1
    f_prev   = f0
    f_actual = f1

    while True:
        if (f_actual - f_prev) == 0:
            return {"error": "Error: División por cero (f(xi) = f(xi-1))."}

        c_nuevo = c_actual - (f_actual * (c_actual - c_prev)) / (f_actual - f_prev)
        f_nuevo = f(c_nuevo)
        if f_nuevo is None:
            return {"error": f"Error evaluando f({c_nuevo:.6f})."}

        # Error relativo porcentual (siempre calculable desde la primera iteración)
        if c_nuevo != 0:
            error_rp  = abs((c_nuevo - c_actual) / c_nuevo) * 100.0
            error_str = f"{error_rp:.6f}%"
        else:
            error_rp  = 0.0
            error_str = "0.000000%"
        
        resultados.append({
            'iter': iteracion,
            'ci':   f"{c_nuevo:.7f}",
            'fci':  f"{f_nuevo:.7f}",
            'error': error_str
        })
        
        if error_rp < tol or f_nuevo == 0:
            raiz_encontrada = c_nuevo
            break

        c_prev, f_prev     = c_actual, f_actual
        c_actual, f_actual = c_nuevo,  f_nuevo
        iteracion += 1
        if iteracion > 201:
            return {"error": "Error: El método no convergió en 200 iteraciones."}

    return {"resultados": resultados, "raiz": raiz_encontrada, "mensaje": f"Secante | Raíz: {raiz_encontrada:.8f}"}
