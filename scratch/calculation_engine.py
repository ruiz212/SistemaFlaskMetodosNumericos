import sympy as sp
import numpy as np

def analysis_fixed_point(f_str, x0_est):
    x = sp.symbols('x')
    z = sp.symbols('z_dummy')
    
    try:
        f_expr = sp.sympify(f_str.replace('^', '**'))
    except Exception as e:
        return f"Error: {e}"
        
    g_list = []
    # Base: x = x + f(x) and x = x - f(x)
    g_list.append(x + f_expr)
    g_list.append(x - f_expr)
    
    # Term isolation
    if isinstance(f_expr, sp.Add):
        for term in f_expr.args:
            if term.has(x):
                remaining = f_expr - term
                remaining_z = remaining.subs(x, z)
                try:
                    sols = sp.solve(sp.Eq(term, -remaining_z), x)
                    for s in sols:
                        g_list.append(s.subs(z, x))
                except:
                    continue
    
    # Factoring isolation
    try:
        const_term = f_expr.as_coeff_Add()[0]
        poly_part = f_expr - const_term
        if poly_part.has(x):
            g_list.append(-const_term / (poly_part / x))
    except:
        pass

    unique_gs = []
    seen = set()
    for g in g_list:
        try:
            gs = sp.simplify(g)
            if str(gs) not in seen and not gs.is_constant():
                unique_gs.append(gs)
                seen.add(str(gs))
        except:
            continue
            
    print(f"Analysis for f(x) = {f_str} = 0")
    print(f"Estimated x0 = {x0_est}")
    print("-" * 40)
    
    results = []
    for i, g in enumerate(unique_gs):
        dg = sp.diff(g, x)
        val_dg = abs(float(dg.evalf(subs={x: x0_est})))
        converges = val_dg < 1
        
        results.append({
            'num': i+1,
            'g': g,
            'dg': dg,
            'val_dg': val_dg,
            'converges': converges
        })
        
        print(f"g{i+1}(x) = {g}")
        print(f"g'{i+1}(x) = {dg}")
        print(f"|g'{i+1}({x0_est})| = {val_dg:.6f} -> {'Converges' if converges else 'Diverges'}")
        print("-" * 20)
        
    return results

analysis_fixed_point("x**2 - 3*x + exp(x) - 2", 1.0)
