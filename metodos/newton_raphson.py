def newton_raphson(ci, tol, f, df, cfg=None):
    if cfg is None: cfg = {}
    iter_max = int(cfg.get('nl_iter_max', 500))
    error_mode = cfg.get('nl_error_mode', 'relativo')
    resultados = []
    iteracion = 1          # Convención: empieza en iteración 1
    ci_anterior = None     # Para detectar primera iteración
    raiz_encontrada = None

    while True:
        f_ci  = f(ci)
        df_ci = df(ci)
        
        if f_ci is None or df_ci is None:
            return {"error": "Error matemático evaluando la función o su derivada."}
        
        # Manejo de números complejos (tomar parte real)
        f_ci = f_ci.real if isinstance(f_ci, complex) else f_ci
        df_ci = df_ci.real if isinstance(df_ci, complex) else df_ci

        if df_ci == 0:
            return {"error": "Error: La derivada es cero. El método no puede continuar."}
        
        ci_mas_1 = ci - (f_ci / df_ci)   # Fórmula de Newton-Raphson

        # Error evaluation
        if error_mode == 'absoluto':
            err_val = abs(ci_mas_1 - ci)
            error_str = f"{err_val:.15f}"
        else:
            if ci_mas_1 != 0:
                err_val = abs((ci_mas_1 - ci) / ci_mas_1)
                error_str = f"{err_val * 100.0:.15f}%"
            else:
                err_val = 0.0
                error_str = "0.000000%"
        
        resultados.append({
            'iter': iteracion,
            'ci':    f"{ci:.15f}",
            'fci':   f"{f_ci:.15f}",
            'dfci':  f"{df_ci:.15f}",
            'cimas1': f"{ci_mas_1:.15f}",
            'error': error_str
        })
        
        if err_val < tol or f_ci == 0:
            raiz_encontrada = ci_mas_1
            break

        ci_anterior = ci
        ci = ci_mas_1
        iteracion += 1
        if iteracion > iter_max:
            return {"error": f"Error: El método no convergió en {iter_max} iteraciones (posible divergencia)."}

    return {"resultados": resultados, "raiz": raiz_encontrada, "mensaje": f"Newton-Raphson | Raíz: {raiz_encontrada:.8f}"}
