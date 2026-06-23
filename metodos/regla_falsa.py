def regla_falsa(a, b, tol, f, cfg=None):
    if cfg is None: cfg = {}
    iter_max = int(cfg.get('nl_iter_max', 500))
    error_mode = cfg.get('nl_error_mode', 'relativo')
    resultados = []
    fa, fb = f(a), f(b)
    if fa is None or fb is None: 
        return {"error": "Error en evaluación."}
    if fa * fb >= 0: 
        return {"error": "No hay cambio de signo entre a y b."}
    
    c_anterior = None      # None indica primera iteración
    i = 1                  # Convención Chapra: empieza en 1
    raiz_encontrada = None

    while True:
        fa, fb = f(a), f(b)
        
        # Manejo de números complejos (tomar parte real)
        fa = fa.real if isinstance(fa, complex) else fa
        fb = fb.real if isinstance(fb, complex) else fb

        c_actual = (a * fb - b * fa) / (fb - fa)   # Interpolación lineal
            
        fc = f(c_actual)
        if fc is None:
            return {"error": f"Error evaluando f({c_actual:.15f})."}
        fc = fc.real if isinstance(fc, complex) else fc
        prueba_signo = fa * fc
        
        if c_anterior is None:
            err_val = float('inf')
            error_str = "---"
        else:
            if error_mode == 'absoluto':
                err_val = abs(c_actual - c_anterior)
                error_str = f"{err_val:.15f}"
            else:
                if c_actual != 0:
                    err_val = abs((c_actual - c_anterior) / c_actual)
                    error_str = f"{err_val * 100.0:.15f}%"
                else:
                    err_val = 0.0
                    error_str = "0.000000%"
        
        ea = abs(b - a)
        
        resultados.append({
            'iter': i, 'a': f"{a:.15f}", 'c': f"{c_actual:.15f}", 'b': f"{b:.15f}",
            'fa': f"{fa:.15f}", 'fc': f"{fc:.15f}", 'fb': f"{fb:.15f}", 
            'prueba': f"{prueba_signo:.15f}", 'ea': f"{ea:.15f}", 'error': error_str
        })
        
        if (c_anterior is not None and err_val < tol) or fc == 0:
            raiz_encontrada = c_actual
            break
            
        if prueba_signo < 0:
            b = c_actual
        else:
            a = c_actual

        c_anterior = c_actual
        i += 1
        if i > iter_max:
            return {"error": f"Límite de iteraciones alcanzado ({iter_max})."}
            
    return {"resultados": resultados, "raiz": raiz_encontrada, "mensaje": f"Regla Falsa finalizado | Raíz: {raiz_encontrada:.8f}"}
