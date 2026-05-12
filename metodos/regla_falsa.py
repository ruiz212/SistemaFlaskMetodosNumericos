def regla_falsa(a, b, tol, f):
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
            return {"error": f"Error evaluando f({c_actual:.6f})."}
        fc = fc.real if isinstance(fc, complex) else fc
        prueba_signo = fa * fc
        
        if c_anterior is None:
            error_rp  = float('inf')
            error_str = "---"
        elif c_actual != 0:
            error_rp  = abs((c_actual - c_anterior) / c_actual) * 100.0
            error_str = f"{error_rp:.6f}%"
        else:
            error_rp  = 0.0
            error_str = "0.000000%"
        
        resultados.append({
            'iter': i, 'a': f"{a:.6f}", 'b': f"{b:.6f}", 'c': f"{c_actual:.6f}",
            'fa': f"{fa:.6f}", 'fb': f"{fb:.6f}", 'fc': f"{fc:.6f}", 
            'prueba': f"{prueba_signo:.6f}", 'error': error_str
        })
        
        if (c_anterior is not None and error_rp < tol) or fc == 0:
            raiz_encontrada = c_actual
            break
            
        if prueba_signo < 0:
            b = c_actual
        else:
            a = c_actual

        c_anterior = c_actual
        i += 1
        if i > 501:
            return {"error": "Límite de iteraciones alcanzado (500)."}
            
    return {"resultados": resultados, "raiz": raiz_encontrada, "mensaje": f"Regla Falsa finalizado | Raíz: {raiz_encontrada:.8f}"}
