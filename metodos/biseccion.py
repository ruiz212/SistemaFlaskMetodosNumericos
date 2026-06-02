def biseccion(a, b, tol, f):
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
            return {"error": f"Error de dominio matemático evaluando en x={c_actual:.6f}."}
        fc = fc.real if isinstance(fc, complex) else fc
            
        prueba_signo = fa * fc
        
        # Error relativo porcentual — "---" solo en la primera iteración (sin punto anterior)
        if c_anterior is None:
            error_rp  = float('inf')
            error_str = "---"
        elif c_actual != 0:
            error_rp  = abs((c_actual - c_anterior) / c_actual) * 100.0
            error_str = f"{error_rp:.6f}%"
        else:
            error_rp  = 0.0
            error_str = "0.000000%"
        
        ea = abs(b - a)
        
        resultados.append({
            'iter': i, 'a': f"{a:.6f}", 'c': f"{c_actual:.6f}", 'b': f"{b:.6f}",
            'fa': f"{fa:.6f}", 'fc': f"{fc:.6f}", 'fb': f"{fb:.6f}", 
            'prueba': f"{prueba_signo:.6f}", 'ea': f"{ea:.6f}", 'error': error_str
        })
        
        # Condición de parada: error < tol (desde iter 2 en adelante) o raíz exacta
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
            
    return {"resultados": resultados, "raiz": raiz_encontrada, "mensaje": f"Bisección finalizado | Raíz: {raiz_encontrada:.8f}"}
