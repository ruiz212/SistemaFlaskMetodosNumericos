def newton_raphson(ci, tol, f, df):
    resultados = []
    iteracion = 1          # Convención: empieza en iteración 1
    ci_anterior = None     # Para detectar primera iteración
    raiz_encontrada = None

    while True:
        f_ci  = f(ci)
        df_ci = df(ci)
        if f_ci is None or df_ci is None:
            return {"error": "Error matemático evaluando la función o su derivada."}
        if df_ci == 0:
            return {"error": "Error: La derivada es cero. El método no puede continuar."}
        
        ci_mas_1 = ci - (f_ci / df_ci)   # Fórmula de Newton-Raphson

        # Error relativo porcentual
        if ci_anterior is None:
            # Primera iteración: se compara ci+1 vs ci (el punto inicial dado)
            if ci_mas_1 != 0:
                error_rp  = abs((ci_mas_1 - ci) / ci_mas_1) * 100.0
                error_str = f"{error_rp:.6f}%"
            else:
                error_rp  = 0.0
                error_str = "0.000000%"
        else:
            if ci_mas_1 != 0:
                error_rp  = abs((ci_mas_1 - ci) / ci_mas_1) * 100.0
                error_str = f"{error_rp:.6f}%"
            else:
                error_rp  = 0.0
                error_str = "0.000000%"
        
        resultados.append({
            'iter': iteracion,
            'ci':    f"{ci:.6f}",
            'fci':   f"{f_ci:.6f}",
            'dfci':  f"{df_ci:.6f}",
            'cimas1': f"{ci_mas_1:.6f}",
            'error': error_str
        })
        
        if error_rp < tol or f_ci == 0:
            raiz_encontrada = ci_mas_1
            break

        ci_anterior = ci
        ci = ci_mas_1
        iteracion += 1
        if iteracion > 201:
            return {"error": "Error: El método no convergió en 200 iteraciones (posible divergencia)."}

    return {"resultados": resultados, "raiz": raiz_encontrada, "mensaje": f"Newton-Raphson | Raíz: {raiz_encontrada:.8f}"}
