def newton_raphson(ci, tol, f, df):
    resultados = []
    iteracion = 0
    raiz_encontrada = None
    while True:
        f_ci, df_ci = f(ci), df(ci)
        if f_ci is None or df_ci is None: return {"error": "Error matemático."}
        if df_ci == 0: return {"error": "Error: Derivada cero."}
        
        ci_mas_1 = ci - (f_ci / df_ci)
        error_rp = abs((ci_mas_1 - ci) / ci_mas_1) * 100.0 if (iteracion > 0 and ci_mas_1 != 0) else 100.0
        error_str = f"{error_rp:.6f}%" if iteracion > 0 else "---"
        
        resultados.append({
            'iter': iteracion, 'ci': f"{ci:.6f}", 'fci': f"{f_ci:.6f}",
            'dfci': f"{df_ci:.6f}", 'cimas1': f"{ci_mas_1:.6f}", 'error': error_str
        })
        
        if error_rp < tol or f_ci == 0:
            raiz_encontrada = ci_mas_1
            break
        ci = ci_mas_1
        iteracion += 1
        if iteracion > 200: return {"error": "Error: divergencia."}
    return {"resultados": resultados, "raiz": raiz_encontrada, "mensaje": f"Newton-Raphson | Raíz: {raiz_encontrada:.8f}"}
