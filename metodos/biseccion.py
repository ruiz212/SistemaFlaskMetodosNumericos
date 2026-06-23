def biseccion(a, b, tol, f, cfg=None):
    if cfg is None: cfg = {}
    iter_max = int(cfg.get('nl_iter_max', 500))
    error_mode = cfg.get('nl_error_mode', 'relativo')
    resultados = []
    fa, fb = f(a), f(b)
    
    if fa is None or fb is None: 
        return {"error": "Error matemático: Evaluación fallida (posible asíntota o división por cero)."}
    if (isinstance(fa, complex) and fa.imag != 0) or (isinstance(fb, complex) and fb.imag != 0):
        return {"error": "Error de dominio matemático: La función arroja números imaginarios."}
        
    fa = fa.real if isinstance(fa, complex) else fa
    fb = fb.real if isinstance(fb, complex) else fb

    if fa * fb > 0: 
        return {"error": "No hay cambio de signo: f(a) y f(b) tienen el mismo signo."}
    elif fa * fb == 0:
        if fa == 0: return {"resultados": [], "raiz": a, "mensaje": f"Raíz exacta encontrada en el extremo a={a}"}
        if fb == 0: return {"resultados": [], "raiz": b, "mensaje": f"Raíz exacta encontrada en el extremo b={b}"}
    
    c_anterior = None      # None indica que es la primera iteración
    i = 1                  # Las iteraciones arrancan en 1 (convención Chapra)
    raiz_encontrada = None

    while True:
        fa, fb = f(a), f(b)
        c_actual = (a + b) / 2.0
            
        fc = f(c_actual)
        if fc is None or (isinstance(fc, complex) and fc.imag != 0):
            return {"error": f"Error de dominio matemático evaluando en x={c_actual:.15f}."}
        fc = fc.real if isinstance(fc, complex) else fc
            
        prueba_signo = fa * fc
        
        # Error evaluation
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
        
        # Condición de parada: error < tol (desde iter 2 en adelante) o raíz exacta
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
            
    return {"resultados": resultados, "raiz": raiz_encontrada, "mensaje": f"Bisección finalizado | Raíz: {raiz_encontrada:.8f}"}
