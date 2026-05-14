import math
import cmath
import numpy as np

def fmt_c(val):
    if isinstance(val, complex):
        if abs(val.imag) < 1e-10: return f"{val.real:.5f}"
        return f"{val.real:.5f}{'+' if val.imag >=0 else '-'}{abs(val.imag):.5f}j"
    return f"{val:.5f}"

def metodo_muller(x0, x1, x2, tol_porcentaje, a_coefs):
    resultados = []
    consola = []
    
    if a_coefs is None:
        return {"error": "Se requieren coeficientes."}
        
    def f_eval(x_val):
        return complex(sum(c_val * (x_val ** i) for i, c_val in enumerate(a_coefs)))
        
    iteracion = 1
    max_iter = 100
    consola.append("=== INICIANDO MÜLLER ===")
    
    # x0, x1, x2 son los valores iniciales
    # x3 será el primer valor calculado
    x_prev2, x_prev1, x_curr = x0, x1, x2
    
    while iteracion <= max_iter:
        h0 = x_prev1 - x_prev2
        h1 = x_curr - x_prev1
        f0, f1, f2 = f_eval(x_prev2), f_eval(x_prev1), f_eval(x_curr)
        
        d0 = (f1 - f0) / h0 if h0 != 0 else 0
        d1 = (f2 - f1) / h1 if h1 != 0 else 0
        a = (d1 - d0) / (h1 + h0) if (h1 + h0) != 0 else 0
        b = a * h1 + d1
        c = f2
        
        rad = cmath.sqrt(b**2 - 4*a*c)
        den = (b + rad) if abs(b + rad) > abs(b - rad) else (b - rad)
            
        if den == 0:
            dx = 0
            consola.append("Advertencia: Denominador cero.")
        else:
            dx = -2 * c / den
            
        x_next = x_curr + dx
        
        # Error relativo porcentual comparando con la aproximación anterior
        if abs(x_next) > 0:
            error_rp = abs((x_next - x_curr) / x_next) * 100.0
        else:
            error_rp = 0.0
            
        error_str = f"{error_rp.real:.6f}%"
        condicion = "Finalizar" if error_rp.real < tol_porcentaje else "Continuar"
        
        resultados.append({
            'iter': iteracion, 
            'x1': fmt_c(x_prev2), 'x2': fmt_c(x_prev1), 'x3': fmt_c(x_curr),
            'h0': fmt_c(h0), 'h1': fmt_c(h1), 
            'f1': fmt_c(f0), 'f2': fmt_c(f1), 'f3': fmt_c(f2),
            'd0': fmt_c(d0), 'd1': fmt_c(d1), 
            'a': fmt_c(a), 'b': fmt_c(b), 'c': fmt_c(c),
            'raiz': fmt_c(x_next), 'error': error_str, 'condicion': condicion
        })
        
        if error_rp.real < tol_porcentaje:
            consola.append(f"\nConvergió en {iteracion} iteraciones.")
            res_raiz = x_next
            consola.append(f"=== RAÍZ ENCONTRADA ===\n X = {fmt_c(res_raiz)}")
            break
            
        # Actualizar para la siguiente iteración
        x_prev2, x_prev1, x_curr = x_prev1, x_curr, x_next
        iteracion += 1
        
        if iteracion > max_iter:
            consola.append("Error: divergencia o límite de iteraciones.")
            return {"error": "Divergencia o límite de iteraciones.", "consola": consola}
            
    raiz_str = fmt_c(res_raiz) if 'res_raiz' in locals() else ""
    return {"resultados": resultados, "consola": consola, "raiz": raiz_str, "mensaje": f"Müller finalizado | Raíz: {raiz_str}"}
