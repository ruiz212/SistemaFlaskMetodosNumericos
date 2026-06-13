import re
import sympy as sp
import numpy as np
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
    # Soporte para y mayúscula
    texto = re.sub(r'(?<![A-Za-z_])Y(?![A-Za-z_0-9])', 'y', texto)
    
    local_dict = _locals_sympify()
    local_dict['y'] = sp.Symbol('y')
    local_dict['Y'] = sp.Symbol('y')
    
    expr_simbolica = sp.sympify(texto, locals=local_dict)

    if isinstance(expr_simbolica, sp.core.relational.Relational):
        raise ValueError(
            "La expresión contiene un operador relacional. Ingresa solo la función."
        )

    if modo_angulo == 'deg':
        for fn in (sp.sin, sp.cos, sp.tan, sp.cot, sp.sec, sp.csc):
            expr_simbolica = expr_simbolica.replace(
                fn, lambda arg, f=fn: f(arg * sp.pi / 180)
            )
    return expr_simbolica


@lru_cache(maxsize=64)
def get_cached_compilation(ecuacion_texto, modo_angulo, variables_permitidas=('x',)):
    return compilar_funciones_base(ecuacion_texto, modo_angulo, variables_permitidas)


def compilar_funciones(ecuacion_texto, modo_angulo='rad', variables_permitidas=('x',)):
    return get_cached_compilation(ecuacion_texto, modo_angulo, variables_permitidas)


def compilar_funciones_base(ecuacion_texto, modo_angulo='rad', variables_permitidas=('x',)):
    try:
        expr_simbolica = parse_ecuacion(ecuacion_texto, modo_angulo)
        
        simbolos_permitidos = set(sp.Symbol(v) for v in variables_permitidas)

        vars_libres = expr_simbolica.free_symbols - simbolos_permitidos
        if vars_libres:
            nombres = ', '.join(sorted(str(v) for v in vars_libres))
            raise ValueError(f"Variable(s) desconocida(s): {nombres}")

        if len(variables_permitidas) == 1:
            x_sym = sp.Symbol(variables_permitidas[0])
            derivada_simbolica = sp.diff(expr_simbolica, x_sym)
            funcion_eval  = sp.lambdify(x_sym, expr_simbolica,  'numpy')
            derivada_eval = sp.lambdify(x_sym, derivada_simbolica, 'numpy')
            return True, "Éxito", x_sym, expr_simbolica, derivada_simbolica, funcion_eval, derivada_eval
        else:
            # Para integrales dobles o múltiples variables
            simbolos_tupla = tuple(sp.Symbol(v) for v in variables_permitidas)
            funcion_eval = sp.lambdify(simbolos_tupla, expr_simbolica, 'numpy')
            return True, "Éxito", simbolos_tupla, expr_simbolica, None, funcion_eval, None
            
    except Exception as e:
        return False, str(e), None, None, None, None, None


def evaluar_f(val, expr_simbolica, x_sym, funcion_eval):
    try:
        # Soporte para múltiples variables
        if isinstance(val, (list, tuple)) and isinstance(x_sym, tuple):
            res = funcion_eval(*val)
        else:
            res = funcion_eval(val)
            
        if res is None or not np.isfinite(res).all():
            raise ValueError("Resultado no finito")
        return res
    except Exception:
        try:
            if isinstance(val, (list, tuple)) and isinstance(x_sym, tuple):
                subs_dict = {sym: v for sym, v in zip(x_sym, val)}
                res = expr_simbolica.evalf(subs=subs_dict)
            else:
                res = expr_simbolica.evalf(subs={x_sym: val})
            return complex(res) if res.is_complex else float(res)
        except Exception:
            return None


def evaluar_df(val, derivada_simbolica, x_sym, derivada_eval):
    try:
        res = derivada_eval(val)
        if res is None or not np.isfinite(res).all():
            raise ValueError("Resultado no finito")
        return res
    except Exception:
        try:
            res = derivada_simbolica.evalf(subs={x_sym: val})
            return complex(res) if res.is_complex else float(res)
        except Exception:
            return None
