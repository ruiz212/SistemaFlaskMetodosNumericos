import sympy as sp

def despejar_ecuacion(f_str):
    x = sp.symbols('x')
    try:
        f_str = f_str.replace('^', '**')
        # Handle cases like e**x
        f_str = f_str.replace('e**x', 'exp(x)')
        f_expr = sp.sympify(f_str)
    except Exception as e:
        return {"error": f"Error al procesar la ecuación: {str(e)}"}
    
    g_options = []
    
    # Estrategia 1: x = x + f(x) y x = x - f(x)
    g_options.append(x + f_expr)
    g_options.append(x - f_expr)
    
    # Estrategia 2: Si es una suma, despejar x de cada término que lo contenga
    if isinstance(f_expr, sp.Add):
        print(f"Terms found: {f_expr.args}")
        for term in f_expr.args:
            if term.has(x):
                remaining = f_expr - term
                print(f"Trying to solve term: {term} = {-remaining}")
                try:
                    sols = sp.solve(sp.Eq(term, -remaining), x)
                    print(f"  Solutions for {term}: {sols}")
                    for s in sols:
                        g_options.append(s)
                except Exception as e:
                    print(f"  Error solving {term}: {e}")
                    continue
                    
    # Estrategia 3: Intentar factorizar x y despejar
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
            if g_str not in seen:
                latex_g = sp.latex(g_simp)
                results.append({"expr": g_str, "latex": latex_g})
                seen.add(g_str)
        except:
            continue
            
    return {"despejes": results}

test_eq = "x**2 - 3*x + exp(x) - 2"
res = despejar_ecuacion(test_eq)
print("\nFinal results:")
for d in res['despejes']:
    print(f"g(x) = {d['expr']}")
