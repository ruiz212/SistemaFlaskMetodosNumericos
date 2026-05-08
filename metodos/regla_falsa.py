def regla_falsa(a, b, tol, f):
    resultados = []
    fa, fb = f(a), f(b)
    if fa is None or fb is None: 
        return {"error": "Error en evaluación."}
    if fa * fb >= 0: 
        return {"error": "No hay cambio de signo entre a y b."}
    
    c_anterior = 0
    i = 0
    raiz_encontrada = None
    while True:
        fa, fb = f(a), f(b)
        c_actual = (a * fb - b * fa) / (fb - fa)
            
        fc = f(c_actual)
        prueba_signo = fa * fc
        
        error_rp = abs((c_actual - c_anterior) / c_actual) * 100.0 if (i > 0 and c_actual != 0) else 100.0
        error_str = f"{error_rp:.6f}%" if i > 0 else "---"
        
        resultados.append({
            'iter': i, 'a': f"{a:.6f}", 'b': f"{b:.6f}", 'c': f"{c_actual:.6f}",
            'fa': f"{fa:.6f}", 'fb': f"{fb:.6f}", 'fc': f"{fc:.6f}", 
            'prueba': f"{prueba_signo:.6f}", 'error': error_str
        })
        
        if (i > 0 and error_rp < tol) or fc == 0:
            raiz_encontrada = c_actual
            break
            
        if prueba_signo < 0:
            b = c_actual
        else:
            a = c_actual
        c_anterior = c_actual
        i += 1
        if i > 500:
            return {"error": "Límite de iteraciones alcanzado."}
            
    return {"resultados": resultados, "raiz": raiz_encontrada, "mensaje": f"Regla Falsa finalizado | Raíz: {raiz_encontrada:.8f}"}
