import sympy as sp

def despejar_ecuacion_improved(f_str):
    x = sp.symbols('x')
    z = sp.symbols('z_dummy')
    try:
        f_str = f_str.replace('^', '**')
        # Simple fix for e**x if needed
        if 'exp(' not in f_str and 'e**' in f_str:
             f_str = f_str.replace('e**x', 'exp(x)')
        f_expr = sp.sympify(f_str)
    except Exception as e:
        return {"error": f"Error: {e}"}
    
    g_options = []
    
    # 1. x = x + f(x)
    g_options.append(x + f_expr)
    g_options.append(x - f_expr)
    
    # 2. Term Isolation with Dummy Variable
    if isinstance(f_expr, sp.Add):
        for term in f_expr.args:
            if term.has(x):
                remaining = f_expr - term
                # Replace x in remaining with z
                remaining_z = remaining.subs(x, z)
                try:
                    # Solve term = -remaining_z for x
                    sols = sp.solve(sp.Eq(term, -remaining_z), x)
                    for s in sols:
                        # Replace z back with x
                        g_final = s.subs(z, x)
                        g_options.append(g_final)
                except:
                    continue
                    
    # 3. Factoring strategy
    try:
        const_term = f_expr.as_coeff_Add()[0]
        poly_part = f_expr - const_term
        if poly_part.has(x):
            g_factor = -const_term / (poly_part / x)
            g_options.append(g_factor)
    except:
        pass
        
    # Cleanup
    results = []
    seen = set()
    for g in g_options:
        try:
            g_simp = sp.simplify(g)
            g_str = str(g_simp)
            if g_str not in seen:
                results.append({"expr": g_str, "latex": sp.latex(g_simp)})
                seen.add(g_str)
        except:
            continue
    return results

test_eq = "x**2 - 3*x + exp(x) - 2"
res = despejar_ecuacion_improved(test_eq)
print("\nImproved Results:")
for d in res:
    print(f"x = {d['expr']}")
