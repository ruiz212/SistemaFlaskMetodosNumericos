import math
import cmath

def fmt_c(val):
    if isinstance(val, complex):
        if abs(val.imag) < 1e-10: return f"{val.real:.5f}"
        return f"{val.real:.5f}{'+' if val.imag >=0 else '-'}{abs(val.imag):.5f}j"
    return f"{val:.5f}"

def metodo_horner_newton(a_input, r, tol_porcentaje):
    resultados = []
    consola = []
    tol = tol_porcentaje / 100.0
    consola.append("=== MÉTODO DE HORNER-NEWTON (BIRGE-VIETA) ===\\n")
    
    max_iter = 100
    n = len(a_input) - 1
    a = a_input
    
    iteracion = 1
    error = float('inf')
    
    while error > tol and iteracion <= max_iter:
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

        resultados.append({
            'iter': iteracion, 'r': fmt_c(r), 'pr': fmt_c(p_r), 'ppr': fmt_c(p_prime_r), 'error': f"{error:.6f}"
        })

        r = r_new
        iteracion += 1

    if error <= tol:
        consola.append(f"Convergió en {iteracion-1} iteraciones.")
        consola.append(f"=== RAÍZ ENCONTRADA ===\\n r = {fmt_c(r)}")
    else:
        consola.append("Error: divergencia o se alcanzó el límite máximo de iteraciones sin converger.")
        
    return {"resultados": resultados, "consola": consola}
