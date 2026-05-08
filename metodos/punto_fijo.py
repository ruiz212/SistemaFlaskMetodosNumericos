def punto_fijo(x0, tol, f, force=False, g_prima=None):
    if g_prima is not None and abs(g_prima) >= 1 and not force:
        return {"warning": f"|g'(x0)|={abs(g_prima):.4f} >= 1. ¿Continuar?"}
        
    resultados = []
    x_actual, iteracion = x0, 1
    raiz_encontrada = None
    while True:
        x_nuevo = f(x_actual)
        if x_nuevo is None: return {"error": "Error desbordamiento."}
        error_rp = abs((x_nuevo - x_actual) / x_nuevo) * 100.0 if (iteracion > 1 and x_nuevo != 0) else 100.0
        error_str = f"{error_rp:.6f}%" if iteracion > 1 else "---"
        
        resultados.append({
            'iter': iteracion, 'ci': f"{x_actual:.6f}", 'gci': f"{x_nuevo:.6f}", 'error': error_str
        })
        
        if (iteracion > 1 and error_rp < tol) or x_actual == x_nuevo:
            raiz_encontrada = x_nuevo
            break
        x_actual, iteracion = x_nuevo, iteracion + 1
        if iteracion > 200: return {"error": "Error: divergencia."}
    return {"resultados": resultados, "raiz": raiz_encontrada, "mensaje": f"Punto Fijo | Raíz: {raiz_encontrada:.8f}"}
