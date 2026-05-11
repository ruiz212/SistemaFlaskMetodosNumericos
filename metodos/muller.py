import math
import cmath

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
        
    iteracion = 0
    max_iter = 100
    consola.append("=== INICIANDO MÜLLER ===")
    
    pts = [x0, x1, x2]
    
    while iteracion <= max_iter:
        curr_x0 = pts[iteracion]
        curr_x1 = pts[iteracion+1]
        curr_x2 = pts[iteracion+2]
        
        h0 = curr_x1 - curr_x0
        h1 = curr_x2 - curr_x1
        f0, f1, f2 = f_eval(curr_x0), f_eval(curr_x1), f_eval(curr_x2)
        
        d0 = (f1 - f0) / h0 if h0 != 0 else 0
        d1 = (f2 - f1) / h1 if h1 != 0 else 0
        a = (d1 - d0) / (h1 + h0) if (h1 + h0) != 0 else 0
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
            dx = 0
            consola.append("Advertencia: Denominador cero, asumiendo dx = 0.")
        else:
            dx = -2 * c / den
            
        x3 = curr_x2 + dx
        pts.append(x3)
        
        if iteracion == 0:
            error_rp = 100.0
            error_str = "---"
            condicion = "---"
        else:
            val_k = pts[iteracion]
            val_k_minus_1 = pts[iteracion-1]
            if abs(val_k) > 0:
                error_rp = abs((val_k - val_k_minus_1) / val_k) * 100.0
            else:
                error_rp = 100.0
            error_str = f"{error_rp.real:.6f}"
            condicion = "Finalizar" if error_rp.real < tol_porcentaje else "Continuar"
        
        resultados.append({
            'iter': iteracion, 'x1': fmt_c(curr_x0), 'x2': fmt_c(curr_x1),
            'h0': fmt_c(h0), 'h1': fmt_c(h1), 'f1': fmt_c(f0), 'f2': fmt_c(f1),
            'd0': fmt_c(d0), 'd1': fmt_c(d1), 'a': fmt_c(a), 'b': fmt_c(b), 'c': fmt_c(c),
            'b_plus': fmt_c(b_plus), 'b_minus': fmt_c(b_minus), 'error': error_str, 'condicion': condicion
        })
        
        if iteracion > 0 and error_rp.real < tol_porcentaje:
            consola.append(f"\\nConvergió en {iteracion} iteraciones.")
            res_raiz = pts[iteracion]
            consola.append(f"=== RAÍZ ENCONTRADA ===\\n X = {fmt_c(res_raiz)}")
            break
            
        iteracion += 1
        if iteracion > max_iter:
            consola.append("Error: divergencia o límite de iteraciones.")
            return {"error": "Divergencia o límite de iteraciones.", "consola": consola}
            
    raiz_str = fmt_c(res_raiz) if 'res_raiz' in locals() else ""
    return {"resultados": resultados, "consola": consola, "raiz": raiz_str, "mensaje": f"Müller finalizado | Raíz: {raiz_str}"}
