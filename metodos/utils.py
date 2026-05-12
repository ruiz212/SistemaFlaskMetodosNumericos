import re
import sympy as sp
from functools import lru_cache

# ─── Variable canónica ────────────────────────────────────────────────────────
_x = sp.Symbol('x')


def normalizar_ecuacion(ecuacion_texto: str) -> str:
    """
    Normaliza el texto de la ecuación antes de pasarlo a SymPy.
    - Convierte X mayúscula a x minúscula.
    - Añade el operador * en multiplicaciones implícitas (2x, x(x+1), etc.).
    """
    # 1. Reemplazar X mayúscula (que no forme parte de una palabra) por x
    normalizado = re.sub(r'(?<![A-Za-z_])X(?![A-Za-z_0-9])', 'x', ecuacion_texto)

    # 2. Multiplicación implícita: 2x -> 2*x, 2( -> 2*(
    normalizado = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', normalizado)
    # 3. Cierre de paréntesis seguido de apertura o letra: )x -> )*x, )( -> )*(
    normalizado = re.sub(r'(\))([a-zA-Z\(])', r'\1*\2', normalizado)
    # 4. x seguida de ( si no es una función conocida: x( -> x*(
    normalizado = re.sub(r'(?<![a-zA-Z])x(\()', r'x*\1', normalizado)

    return normalizado


def _locals_sympify():
    """Diccionario de locales extendido para sympify."""
    return {
        'e':   sp.E,
        'E':   sp.E,
        'ln':  sp.log,
        'log': sp.log,
        'sen': sp.sin,  # Soporte para 'sen' (español)
        'tg':  sp.tan,  # Soporte para 'tg' (español)
        'pi':  sp.pi,
        'x':   _x,
        'X':   _x,
    }


def parse_ecuacion(ecuacion_texto, modo_angulo='rad'):
    texto = normalizar_ecuacion(ecuacion_texto)
    expr_simbolica = sp.sympify(texto, locals=_locals_sympify())

    if isinstance(expr_simbolica, sp.core.relational.Relational):
        raise ValueError(
            "La expresión contiene un operador relacional. Ingresa solo f(x)."
        )

    if modo_angulo == 'deg':
        for fn in (sp.sin, sp.cos, sp.tan, sp.cot, sp.sec, sp.csc):
            expr_simbolica = expr_simbolica.replace(
                fn, lambda arg, f=fn: f(arg * sp.pi / 180)
            )
    return expr_simbolica


@lru_cache(maxsize=64)
def get_cached_compilation(ecuacion_texto, modo_angulo):
    """Caché para evitar recompilar la misma ecuación múltiples veces."""
    return compilar_funciones_base(ecuacion_texto, modo_angulo)


def compilar_funciones(ecuacion_texto, modo_angulo='rad'):
    """Wrapper con caché."""
    return get_cached_compilation(ecuacion_texto, modo_angulo)


def compilar_funciones_base(ecuacion_texto, modo_angulo='rad'):
    """Lógica real de compilación."""
    try:
        x_sym = _x
        expr_simbolica = parse_ecuacion(ecuacion_texto, modo_angulo)

        vars_libres = expr_simbolica.free_symbols - {x_sym}
        if vars_libres:
            nombres = ', '.join(sorted(str(v) for v in vars_libres))
            raise ValueError(f"Variable(s) desconocida(s): {nombres}")

        derivada_simbolica = sp.diff(expr_simbolica, x_sym)

        # 'numpy' handles real and complex numbers robustly
        funcion_eval  = sp.lambdify(x_sym, expr_simbolica,  'numpy')
        derivada_eval = sp.lambdify(x_sym, derivada_simbolica, 'numpy')

        return True, "Éxito", x_sym, expr_simbolica, derivada_simbolica, funcion_eval, derivada_eval
    except Exception as e:
        return False, str(e), None, None, None, None, None


def evaluar_f(val, expr_simbolica, x_sym, funcion_eval):
    try:
        return funcion_eval(val)
    except (ValueError, TypeError, ZeroDivisionError, OverflowError):
        try:
            res = expr_simbolica.evalf(subs={x_sym: val})
            return complex(res) if res.is_complex else float(res)
        except Exception:
            return None


def evaluar_df(val, derivada_simbolica, x_sym, derivada_eval):
    try:
        return derivada_eval(val)
    except (ValueError, TypeError, ZeroDivisionError, OverflowError):
        try:
            res = derivada_simbolica.evalf(subs={x_sym: val})
            return complex(res) if res.is_complex else float(res)
        except Exception:
            return None
