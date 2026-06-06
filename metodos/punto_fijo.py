def punto_fijo(x0, tol, f, force=False, g_prima=None, cfg=None):
    if cfg is None: cfg = {}
    iter_max = int(cfg.get('nl_iter_max', 500))
    error_mode = cfg.get('nl_error_mode', 'relativo')
    if g_prima is not None and abs(g_prima) >= 1 and not force:
        return {"warning": f"|g'(x0)| = {abs(g_prima):.15f} >= 1. El método puede divergir. ¿Continuar de todas formas?"}
        
    resultados = []
    x_actual  = x0
    iteracion = 1          # Empieza en 1 (Chapra)
    raiz_encontrada = None

    while True:
        x_nuevo = f(x_actual)
        if x_nuevo is None:
            return {"error": "Error: desbordamiento numérico evaluando g(x)."}
            
        x_nuevo = x_nuevo.real if isinstance(x_nuevo, complex) else x_nuevo

        # Error evaluation
        if error_mode == 'absoluto':
            err_val = abs(x_nuevo - x_actual)
            error_str = f"{err_val:.15f}"
        else:
            if x_nuevo != 0:
                err_val = abs((x_nuevo - x_actual) / x_nuevo) * 100.0
                error_str = f"{err_val:.15f}%"
            else:
                err_val = 0.0
                error_str = "0.000000%"
        
        resultados.append({
            'iter': iteracion,
            'ci':   f"{x_actual:.15f}",
            'gci':  f"{x_nuevo:.15f}",
            'error': error_str
        })
        
        # Condición de parada
        if err_val < tol or x_actual == x_nuevo:
            raiz_encontrada = x_nuevo
            break

        x_actual   = x_nuevo
        iteracion += 1
        if iteracion > iter_max:
            return {"error": f"Error: El método no convergió en {iter_max} iteraciones (posible divergencia)."}

    return {"resultados": resultados, "raiz": raiz_encontrada, "mensaje": f"Punto Fijo | Raíz: {raiz_encontrada:.8f}"}
