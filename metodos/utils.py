import re
import sympy as sp

# ─── Variable canónica ────────────────────────────────────────────────────────
_x = sp.Symbol('x')


def normalizar_ecuacion(ecuacion_texto: str) -> str:
    """
    Normaliza el texto de la ecuación antes de pasarlo a SymPy.

    Reglas aplicadas:
    1. Sustituye la variable 'X' (mayúscula) por 'x' (minúscula), cuidando
       no tocar nombres de funciones como 'exp', 'Xe', etc.
    2. Permite que el usuario escriba 'X + ln(X)' o 'x + ln(x)' indistintamente.
    """
    # Reemplaza 'X' que NO vaya precedida/seguida de letra (para no tocar
    # nombres de funciones que empiecen con X — aunque SymPy no tiene ninguno).
    normalizado = re.sub(r'(?<![A-Za-z_])X(?![A-Za-z_0-9])', 'x', ecuacion_texto)
    return normalizado


def _locals_sympify():
    """Diccionario de locales extendido para sympify."""
    return {
        'e':   sp.E,
        'E':   sp.E,       # por si el usuario escribe E mayúscula para Euler
        'ln':  sp.log,
        'log': sp.log,
        'pi':  sp.pi,
        'x':   _x,
        'X':   _x,         # alias explícito — por si acaso
    }


def parse_ecuacion(ecuacion_texto, modo_angulo='rad'):
    texto = normalizar_ecuacion(ecuacion_texto)
    expr_simbolica = sp.sympify(texto, locals=_locals_sympify())

    # Rechazar expresiones que no sean algebraicas (por ej. Relationals)
    if isinstance(expr_simbolica, sp.core.relational.Relational):
        raise ValueError(
            "La expresión contiene un operador relacional (>=, <=, ==…). "
            "Ingresa solo la función f(x), sin igualdades ni comparaciones."
        )

    if modo_angulo == 'deg':
        for fn in (sp.sin, sp.cos, sp.tan, sp.cot, sp.sec, sp.csc):
            expr_simbolica = expr_simbolica.replace(
                fn, lambda arg, f=fn: f(arg * sp.pi / 180)
            )
    return expr_simbolica


def compilar_funciones(ecuacion_texto, modo_angulo='rad'):
    try:
        x_sym = _x
        expr_simbolica = parse_ecuacion(ecuacion_texto, modo_angulo)

        # Verificar que la expresión solo depende de 'x' (o de ninguna variable)
        vars_libres = expr_simbolica.free_symbols - {x_sym}
        if vars_libres:
            nombres = ', '.join(sorted(str(v) for v in vars_libres))
            raise ValueError(
                f"Variable(s) desconocida(s) en la ecuación: {nombres}. "
                "Usa 'x' como única variable independiente."
            )

        derivada_simbolica = sp.diff(expr_simbolica, x_sym)
        funcion_eval  = sp.lambdify(x_sym, expr_simbolica,  'math')
        derivada_eval = sp.lambdify(x_sym, derivada_simbolica, 'math')
        return True, "Éxito", x_sym, expr_simbolica, derivada_simbolica, funcion_eval, derivada_eval
    except Exception as e:
        return False, str(e), None, None, None, None, None


def evaluar_f(val, expr_simbolica, x_sym, funcion_eval):
    try:
        if isinstance(val, complex):
            return complex(expr_simbolica.evalf(subs={x_sym: val}))
        result = funcion_eval(val)
        if result is None:
            raise ValueError("None")
        return float(result)
    except Exception:
        try:
            return complex(expr_simbolica.evalf(subs={x_sym: val}))
        except Exception:
            return None


def evaluar_df(val, derivada_simbolica, x_sym, derivada_eval):
    try:
        if isinstance(val, complex):
            return complex(derivada_simbolica.evalf(subs={x_sym: val}))
        result = derivada_eval(val)
        if result is None:
            raise ValueError("None")
        return float(result)
    except Exception:
        try:
            return complex(derivada_simbolica.evalf(subs={x_sym: val}))
        except Exception:
            return None
