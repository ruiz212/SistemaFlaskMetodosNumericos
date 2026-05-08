import sympy as sp

def parse_ecuacion(ecuacion_texto, modo_angulo='rad'):
    expr_simbolica = sp.sympify(ecuacion_texto, locals={'e': sp.E, 'ln': sp.log})
    if modo_angulo == 'deg':
        expr_simbolica = expr_simbolica.replace(sp.sin, lambda arg: sp.sin(arg * sp.pi / 180))
        expr_simbolica = expr_simbolica.replace(sp.cos, lambda arg: sp.cos(arg * sp.pi / 180))
        expr_simbolica = expr_simbolica.replace(sp.tan, lambda arg: sp.tan(arg * sp.pi / 180))
        expr_simbolica = expr_simbolica.replace(sp.cot, lambda arg: sp.cot(arg * sp.pi / 180))
        expr_simbolica = expr_simbolica.replace(sp.sec, lambda arg: sp.sec(arg * sp.pi / 180))
        expr_simbolica = expr_simbolica.replace(sp.csc, lambda arg: sp.csc(arg * sp.pi / 180))
    return expr_simbolica

def compilar_funciones(ecuacion_texto, modo_angulo='rad'):
    try:
        x_sym = sp.Symbol('x')
        expr_simbolica = parse_ecuacion(ecuacion_texto, modo_angulo)
        derivada_simbolica = sp.diff(expr_simbolica, x_sym)
        funcion_eval = sp.lambdify(x_sym, expr_simbolica, 'math')
        derivada_eval = sp.lambdify(x_sym, derivada_simbolica, 'math')
        return True, "Éxito", x_sym, expr_simbolica, derivada_simbolica, funcion_eval, derivada_eval
    except Exception as e:
        return False, str(e), None, None, None, None, None

def evaluar_f(val, expr_simbolica, x_sym, funcion_eval):
    try:
        if isinstance(val, complex):
            return complex(expr_simbolica.evalf(subs={x_sym: val}))
        return funcion_eval(val)
    except Exception:
        try: return complex(expr_simbolica.evalf(subs={x_sym: val}))
        except: return None

def evaluar_df(val, derivada_simbolica, x_sym, derivada_eval):
    try:
        if isinstance(val, complex):
            return complex(derivada_simbolica.evalf(subs={x_sym: val}))
        return derivada_eval(val)
    except Exception:
        try: return complex(derivada_simbolica.evalf(subs={x_sym: val}))
        except: return None
