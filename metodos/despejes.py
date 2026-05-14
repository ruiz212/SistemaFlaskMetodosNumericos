import sympy as sp

def despejar_ecuacion(f_str, x0=None):
    """
    Motor de cálculo simbólico de Punto Fijo.
    Sigue reglas estrictas de despeje natural y formateo compacto.
    """
    x = sp.symbols('x')
    z = sp.symbols('z_dummy')
    
    try:
        # Normalización de entrada
        f_str = f_str.replace('^', '**')
        import re
        f_str = re.sub(r'\be\s*\*\*\s*([a-zA-Z0-9_()]+)', r'exp(\1)', f_str)
        f_str = re.sub(r'\be\s*\^\s*([a-zA-Z0-9_()]+)', r'exp(\1)', f_str)
        
        locals_dict = {
            'e':   sp.E, 'E':   sp.E,
            'ln':  sp.log, 'log': sp.log,
            'sen': sp.sin, 'tg':  sp.tan,
            'pi':  sp.pi, 'x':   x,
        }
        f_expr = sp.sympify(f_str, locals=locals_dict)
    except Exception as e:
        return {"error": f"Error: {str(e)}"}
    
    g_options = []
    
    # REGLA: Solo despejar términos existentes (Despejes Naturales)
    # Se omiten x + f(x) y x - f(x) por ser considerados artificios.
    
    if isinstance(f_expr, sp.Add):
        for term in f_expr.args:
            if term.has(x):
                # Aislamos el término tratándolo como independiente
                remaining = f_expr - term
                remaining_z = remaining.subs(x, z)
                try:
                    sols = sp.solve(sp.Eq(term, -remaining_z), x)
                    for s in sols:
                        g_options.append(s.subs(z, x))
                except:
                    continue
    
    results = []
    seen = set()
    
    for g in g_options:
        try:
            # PASO 1: Simplificación del despeje g(x)
            g_simp = sp.simplify(g)
            g_str = str(g_simp)
            
            if g_str not in seen and not g_simp.is_constant():
                # PASO 2: Cálculo de Derivada con Formateo Compacto
                # Usamos cancel() y together() para asegurar denominador común
                dg_raw = sp.diff(g_simp, x)
                dg_simp = sp.cancel(sp.together(dg_raw))
                
                # Evaluación Numérica (Paso 3)
                conv_val = None
                if x0 is not None:
                    try:
                        conv_val = abs(float(dg_simp.evalf(subs={x: x0})))
                    except:
                        conv_val = None
                
                results.append({
                    "expr": g_str.replace('**', '^'),
                    "latex": sp.latex(g_simp),
                    "derivada": sp.latex(dg_simp),
                    "eval": conv_val,
                    "converge": conv_val < 1 if conv_val is not None else None
                })
                seen.add(g_str)
        except:
            continue
            
    return {"despejes": results}

if __name__ == "__main__":
    # Prueba rápida
    test_eq = "x**2 - x - 2"
    print(f"Despejando: {test_eq}")
    res = despejar_ecuacion(test_eq)
    for d in res.get("despejes", []):
        print(f"g(x) = {d['expr']}  => LaTeX: {d['latex']}")
