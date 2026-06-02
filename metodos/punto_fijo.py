def punto_fijo(x0, tol, f, force=False, g_prima=None):
    if g_prima is not None and abs(g_prima) >= 1 and not force:
        return {"warning": f"|g'(x0)| = {abs(g_prima):.4f} >= 1. El método puede divergir. ¿Continuar de todas formas?"}
        
    resultados = []
    x_actual  = x0
    iteracion = 1          # Empieza en 1 (Chapra)
    raiz_encontrada = None

    while True:
        x_nuevo = f(x_actual)
        if x_nuevo is None:
            return {"error": "Error: desbordamiento numérico evaluando g(x)."}
            
        x_nuevo = x_nuevo.real if isinstance(x_nuevo, complex) else x_nuevo

        # Error relativo porcentual — calculable desde la primera iteración
        if x_nuevo != 0:
            error_rp  = abs((x_nuevo - x_actual) / x_nuevo) * 100.0
            error_str = f"{error_rp:.6f}%"
        else:
            error_rp  = 0.0
            error_str = "0.000000%"
        
        resultados.append({
            'iter': iteracion,
            'ci':   f"{x_actual:.6f}",
            'gci':  f"{x_nuevo:.6f}",
            'error': error_str
        })
        
        # Condición de parada
        if error_rp < tol or x_actual == x_nuevo:
            raiz_encontrada = x_nuevo
            break

        x_actual   = x_nuevo
        iteracion += 1
        if iteracion > 201:
            return {"error": "Error: El método no convergió en 200 iteraciones (posible divergencia)."}

    return {"resultados": resultados, "raiz": raiz_encontrada, "mensaje": f"Punto Fijo | Raíz: {raiz_encontrada:.8f}"}
