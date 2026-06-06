import math
import cmath

def fmt_c(val, imag_tol=1e-10):
    if isinstance(val, complex):
        if abs(val.imag) < imag_tol: return f"{val.real:.15f}"
        return f"{val.real:.15f}{'+' if val.imag >=0 else '-'}{abs(val.imag):.15f}j"
    return f"{val:.15f}"

def metodo_horner_newton(a_input, r, tol_porcentaje, cfg=None):
    if cfg is None: cfg = {}
    try:
        imag_tol = float(cfg.get('pol_imag_tol', 1e-10))
    except (ValueError, TypeError):
        imag_tol = 1e-10
    iter_max = int(cfg.get('nl_iter_max', 100))
    
    resultados = []
    consola = []
    tol = tol_porcentaje / 100.0
    consola.append("=== MÉTODO DE HORNER-NEWTON (BIRGE-VIETA) ===\n")
    
    n = len(a_input) - 1
    
    encabezados = ["Iteración", "r_n"]
    for i in range(n, -1, -1):
        encabezados.append(f"b_{i}")
    for i in range(n, 0, -1):
        encabezados.append(f"c_{i}")
    encabezados.extend(["Error", "Condición"])
    n = len(a_input) - 1
    a = a_input
    
    iteracion = 0
    error = float('inf')
    
    while error > tol and iteracion <= iter_max:
        b = [0] * (n + 1)
        b[0] = a[0]
        for i in range(1, n + 1):
            b[i] = a[i] + r * b[i - 1]
        p_r = b[n]

        c = [0] * n
        c[0] = b[0]
        for i in range(1, n):
            c[i] = b[i] + r * c[i - 1]
        p_prime_r = c[n - 1]

        if abs(p_prime_r) == 0:
            consola.append("Derivada cero encontrada. El método falla.")
            return {"error": "La derivada (C_1) es cero, cambie el valor inicial r_0.", "consola": consola}

        r_new = r - (p_r / p_prime_r)
        error = abs(r_new - r)

        fila = [str(iteracion), fmt_c(r, imag_tol)]
        for i in range(n + 1):
            fila.append(fmt_c(b[i], imag_tol))
        for i in range(n):
            fila.append(fmt_c(c[i], imag_tol))
        
        fila.append(f"{error:.15f}")
        fila.append("Cumple" if error <= tol else "")
        
        resultados.append({'data': fila})

        r = r_new
        iteracion += 1

    if error <= tol:
        consola.append(f"Convergió en {iteracion-1} iteraciones.")
        consola.append(f"=== RAÍZ ENCONTRADA ===\n r = {fmt_c(r, imag_tol)}")
    else:
        consola.append("Error: divergencia o se alcanzó el límite máximo de iteraciones sin converger.")
        
    return {"resultados": resultados, "consola": consola, "encabezados": encabezados}
