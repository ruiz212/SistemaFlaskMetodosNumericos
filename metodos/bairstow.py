import math

def metodo_bairstow(a_input, tol_porcentaje, r0_manual=None, s0_manual=None):
    resultados = []
    consola = []
    a = a_input[::-1] 
    max_iter = 100
    raices_totales = []
    n = len(a) - 1
    grado_inicial = n 
    
    usar_manual = (r0_manual is not None and s0_manual is not None and str(r0_manual).strip() != '' and str(s0_manual).strip() != '')
    if usar_manual:
        try:
            r0_manual = float(r0_manual)
            s0_manual = float(s0_manual)
        except ValueError:
            usar_manual = False
    
    encabezados = ['Iter']
    for i in range(grado_inicial, -1, -1): encabezados.append(f'b_{i}')
    for i in range(grado_inicial, 0, -1): encabezados.append(f'c_{i}')
    encabezados.extend(['Δr', 'Δs', 'r', 's', 'Err_r(%)', 'Err_s(%)', 'X1', 'X2'])
    
    consola.append(f"=== INICIANDO BAIRSTOW (Grado {n}) ===")
    
    r_init, s_init = None, None
    
    while n >= 3:
        if usar_manual:
            r, s = r0_manual, s0_manual
            tipo = "MANUALES"
            usar_manual = False
        else:
            if abs(a[0]) < abs(a[n]):
                r, s = a[1]/a[2], a[0]/a[2]
                tipo = "PEQUEÑAS"
            else:
                r, s = a[n-1]/a[n], a[n-2]/a[n]
                tipo = "GRANDES"
            
        if r_init is None and s_init is None:
            r_init, s_init = r, s
            
        consola.append(f"\nPolinomio Grado {n}. Usando fór. {tipo} (r0={r:.4f}, s0={s:.4f})")
        
        for it in range(1, max_iter + 1):
            b = [0.0] * (n + 1)
            c = [0.0] * (n + 1)
            
            b[n] = a[n]
            b[n-1] = a[n-1] + r * b[n]
            for i in range(n-2, -1, -1): b[i] = a[i] + r * b[i+1] + s * b[i+2]
                
            c[n] = b[n]
            c[n-1] = b[n-1] + r * c[n]
            for i in range(n-2, 0, -1): c[i] = b[i] + r * c[i+1] + s * c[i+2]
            
            den = c[2]**2 - c[1]*c[3]
            if den == 0:
                consola.append("Error: Denominador cero.")
                return {"error": "Denominador cero.", "consola": consola}
                
            dr = (b[0]*c[3] - b[1]*c[2]) / den
            ds = (b[1]*c[1] - b[0]*c[2]) / den
            
            r_nuevo, s_nuevo = r + dr, s + ds
            err_r = (abs(dr / r_nuevo) * 100) if r_nuevo != 0 else 100.0
            err_s = (abs(ds / s_nuevo) * 100) if s_nuevo != 0 else 100.0
            
            disc = r**2 + 4*s
            if disc >= 0:
                x1 = f"{(r + math.sqrt(disc)) / 2:.4f}"
                x2 = f"{(r - math.sqrt(disc)) / 2:.4f}"
            else:
                x1 = f"{r/2:.4f}+{math.sqrt(-disc)/2:.4f}i"
                x2 = f"{r/2:.4f}-{math.sqrt(-disc)/2:.4f}i"
            
            fila = [str(it)]
            for i in range(grado_inicial, -1, -1): fila.append(f"{b[i]:.4f}" if i <= n else "0.0")
            for i in range(grado_inicial, 0, -1): fila.append(f"{c[i]:.4f}" if i <= n else "0.0")
            fila.extend([f"{dr:.4f}", f"{ds:.4f}", f"{r_nuevo:.4f}", f"{s_nuevo:.4f}", 
                            f"{err_r:.4f}%", f"{err_s:.4f}%", x1, x2])
            
            resultados.append({'is_sep': False, 'data': fila})
            
            r, s = r_nuevo, s_nuevo
            
            # Criterio de paro del cuaderno: b0 y b1 aproximadamente cero
            # o el error relativo es menor a la tolerancia
            if (abs(b[0]) <= tol_porcentaje and abs(b[1]) <= tol_porcentaje) or (err_r < tol_porcentaje and err_s < tol_porcentaje):
                break
        
        raices_totales.extend([x1, x2])
        a = b[2:n+1]
        n = len(a) - 1
        # Formatear el divisor matemático: x^2 - rx - s
        r_term = f"- {r:.4f}x" if r > 0 else (f"+ {abs(r):.4f}x" if r < 0 else "")
        s_term = f"- {s:.4f}" if s > 0 else (f"+ {abs(s):.4f}" if s < 0 else "")
        divisor_str = f"x^2 {r_term} {s_term}".replace("  ", " ").strip()
        
        # Formatear polinomio deflactado de mayor a menor grado
        terminos_def = []
        for i in range(len(a)-1, -1, -1):
            coef = a[i]
            signo = " + " if coef >= 0 and terminos_def else (" - " if terminos_def else ("-" if coef < 0 else ""))
            val = abs(coef)
            if i == 0:
                terminos_def.append(f"{signo}{val:.4f}")
            elif i == 1:
                terminos_def.append(f"{signo}{val:.4f}x")
            else:
                terminos_def.append(f"{signo}{val:.4f}x^{i}")
        pol_str = "".join(terminos_def)

        consola.append(f">> Polinomio Divisor: {divisor_str}")
        consola.append(f">> Polinomio Deflactado: {pol_str}")
        
        resultados.append({'is_sep': True})
        
    if n == 2:
        rf, sf = -a[1]/a[2], -a[0]/a[2]
        disc = rf**2 + 4*sf
        if disc >= 0:
            raices_totales.extend([f"{(rf + math.sqrt(disc)) / 2:.4f}", f"{(rf - math.sqrt(disc)) / 2:.4f}"])
        else:
            raices_totales.extend([f"{rf/2:.4f}+{math.sqrt(-disc)/2:.4f}i", f"{rf/2:.4f}-{math.sqrt(-disc)/2:.4f}i"])
    elif n == 1:
        raices_totales.append(f"{-a[0]/a[1]:.4f}")
        
    consola.append("\n=== RAÍCES FINALES ===")
    for i, raiz in enumerate(raices_totales):
        consola.append(f" X_{i+1} = {raiz}")
        
    return {"resultados": resultados, "consola": consola, "encabezados": encabezados, "r_init": r_init, "s_init": s_init}
