def secante(x0, x1, tol, f, cfg=None):
    if cfg is None: cfg = {}
    iter_max = int(cfg.get('nl_iter_max', 500))
    error_mode = cfg.get('nl_error_mode', 'relativo')
    resultados = []
    raiz_encontrada = None

    # Evaluar los puntos iniciales
    f0 = f(x0)
    f1 = f(x1)
    
    if f0 is None or f1 is None:
        return {"error": "Error evaluando la función en los puntos iniciales."}

    # Manejo de números complejos (tomar parte real si existe)
    f0 = f0.real if isinstance(f0, complex) else f0
    f1 = f1.real if isinstance(f1, complex) else f1

    # Registrar puntos iniciales en el historial (Iter 0 e Iter 1)
    resultados.append({
        'iter': 0,
        'ci':   f"{x0:.15f}",
        'fci':  f"{f0:.15f}",
        'error': "---"
    })
    resultados.append({
        'iter': 1,
        'ci':   f"{x1:.15f}",
        'fci':  f"{f1:.15f}",
        'error': "---"
    })

    # Comenzar iteraciones para encontrar x2, x3...
    iteracion = 2
    c_prev   = x0
    c_actual = x1
    f_prev   = f0
    f_actual = f1

    while True:
        denominador = f_actual - f_prev
        if denominador == 0:
            return {"error": "Error: División por cero (f(xi) = f(xi-1)). El método se detuvo."}

        # Fórmula de la Secante
        c_nuevo = c_actual - (f_actual * (c_actual - c_prev)) / denominador
        f_nuevo = f(c_nuevo)
        
        if f_nuevo is None:
            return {"error": f"Error evaluando f({c_nuevo:.15f})."}
        
        f_nuevo = f_nuevo.real if isinstance(f_nuevo, complex) else f_nuevo

        # Error evaluation
        if error_mode == 'absoluto':
            err_val = abs(c_nuevo - c_actual)
            error_str = f"{err_val:.15f}" if iteracion > 2 else "---"
        else:
            if c_nuevo != 0:
                err_val = abs((c_nuevo - c_actual) / c_nuevo)
                error_str = f"{err_val * 100.0:.15f}%" if iteracion > 2 else "---"
            else:
                err_val = 0.0
                error_str = "0.000000%" if iteracion > 2 else "---"
        
        resultados.append({
            'iter': iteracion,
            'ci':   f"{c_nuevo:.15f}",
            'fci':  f"{f_nuevo:.15f}",
            'error': error_str
        })
        
        # Condición de parada
        if err_val < tol or f_nuevo == 0:
            raiz_encontrada = c_nuevo
            break

        # Actualizar para la siguiente iteración
        c_prev, f_prev     = c_actual, f_actual
        c_actual, f_actual = c_nuevo,  f_nuevo
        iteracion += 1
        
        if iteracion > iter_max + 1:
            return {"error": f"Error: El método no convergió en {iter_max} iteraciones."}

    return {"resultados": resultados, "raiz": raiz_encontrada, "mensaje": f"Secante | Raíz: {raiz_encontrada:.8f}"}
