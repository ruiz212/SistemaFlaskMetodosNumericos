import sympy as sp
import re

def despejar_ecuacion(f_str):
    x = sp.symbols('x')
    z = sp.symbols('z_dummy')
    
    try:
        f_str = f_str.replace('^', '**')
        f_str = re.sub(r'\be\s*\*\*\s*([a-zA-Z0-9_()]+)', r'exp(\1)', f_str)
        f_str = re.sub(r'\be\s*\^\s*([a-zA-Z0-9_()]+)', r'exp(\1)', f_str)
        
        # Use the same locals as the main app
        locals_dict = {
            'e':   sp.E,
            'E':   sp.E,
            'ln':  sp.log,
            'log': sp.log,
            'sen': sp.sin,
            'tg':  sp.tan,
            'pi':  sp.pi,
            'x':   x,
        }
        f_expr = sp.sympify(f_str, locals=locals_dict)
    except Exception as e:
        return {"error": f"Error: {e}"}
    
    g_options = []
    g_options.append(x + f_expr)
    g_options.append(x - f_expr)
    
    if isinstance(f_expr, sp.Add):
        for term in f_expr.args:
            if term.has(x):
                remaining = f_expr - term
                remaining_z = remaining.subs(x, z)
                try:
                    sols = sp.solve(sp.Eq(term, -remaining_z), x)
                    for s in sols:
                        g_final = s.subs(z, x)
                        g_options.append(g_final)
                except:
                    continue
                    
    try:
        const_term = f_expr.as_coeff_Add()[0]
        poly_part = f_expr - const_term
        if poly_part.has(x):
            g_factor = -const_term / (poly_part / x)
            g_options.append(g_factor)
    except:
        pass
    
    results = []
    seen = set()
    for g in g_options:
        try:
            g_simp = sp.simplify(g)
            g_str = str(g_simp)
            if g_str not in seen and not g_simp.is_constant():
                results.append(g_str)
                seen.add(g_str)
        except:
            continue
    return results

test_eq = "x**2 - 3*x + e**x - 2"
res = despejar_ecuacion(test_eq)
print(f"Results for {test_eq}:")
for r in res:
    print(f"  x = {r}")
