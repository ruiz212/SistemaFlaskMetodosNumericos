import math
import cmath

def fmt_c(val):
    if isinstance(val, complex):
        if abs(val.imag) < 1e-10: return f"{val.real:.5f}"
        return f"{val.real:.5f}{'+' if val.imag >=0 else '-'}{abs(val.imag):.5f}j"
    return f"{val:.5f}"

def metodo_muller(x0, x1, x2, tol_porcentaje, a_coefs=None, f_eval_ext=None):
    resultados = []
    consola = []
    
    if f_eval_ext is not None:
        def f_eval(x_val):
            val = f_eval_ext(x_val)
            if val is None: raise ValueError("Error al evaluar la función.")
            return complex(val)
    elif a_coefs is not None:
        def f_eval(x_val):
            return complex(sum(c_val * (x_val ** i) for i, c_val in enumerate(a_coefs)))
    else:
        return {"error": "Se requieren coeficientes o una función evaluadora."}
        
    iteracion = 0
    max_iter = 100
    consola.append("=== INICIANDO MÜLLER ===")
    
    while iteracion <= max_iter:
        h0 = x1 - x0
        h1 = x2 - x1
        f0, f1, f2 = f_eval(x0), f_eval(x1), f_eval(x2)
        
        if h0 == 0 or h1 == 0:
            consola.append("Error: h0 o h1 es cero.")
            return {"error": "h0 o h1 es cero.", "consola": consola}
            
        d0 = (f1 - f0) / h0
        d1 = (f2 - f1) / h1
        a = (d1 - d0) / (h1 + h0)
        b = a * h1 + d1
        c = f2
        
        rad = cmath.sqrt(b**2 - 4*a*c)
        b_plus = b + rad
        b_minus = b - rad
        
        if abs(b_plus) > abs(b_minus):
            den = b_plus
        else:
            den = b_minus
            
        if den == 0:
            consola.append("Error: Denominador cero.")
            return {"error": "Denominador cero.", "consola": consola}
            
        dx = -2 * c / den
        x3 = x2 + dx
        
        error_rp = abs(dx / x3) * 100.0 if abs(x3) > 0 else 100.0
        f3 = f_eval(x3)
        error_str = f"{error_rp.real:.5f}%" if iteracion > 0 else "---"
        
        resultados.append({
            'iter': iteracion, 'x1': fmt_c(x1), 'x2': fmt_c(x2),
            'h0': fmt_c(h0), 'h1': fmt_c(h1), 'f1': fmt_c(f1), 'f2': fmt_c(f2),
            'd0': fmt_c(d0), 'd1': fmt_c(d1), 'a': fmt_c(a), 'b': fmt_c(b), 'c': fmt_c(c),
            'b_plus': fmt_c(b_plus), 'b_minus': fmt_c(b_minus), 'error': error_str
        })
        
        if error_rp < tol_porcentaje or abs(f3) == 0:
            consola.append(f"\\nConvergió en {iteracion} iteraciones.")
            consola.append(f"=== RAÍZ ENCONTRADA ===\\n X = {fmt_c(x3)}")
            res_raiz = x3
            break
            
        x0, x1, x2 = x1, x2, x3
        iteracion += 1
        if iteracion > max_iter:
            consola.append("Error: divergencia o límite de iteraciones.")
            return {"error": "Divergencia o límite de iteraciones.", "consola": consola}
            
    raiz_str = fmt_c(res_raiz) if 'res_raiz' in locals() else ""
    return {"resultados": resultados, "consola": consola, "raiz": raiz_str, "mensaje": f"Müller finalizado | Raíz: {raiz_str}"}
