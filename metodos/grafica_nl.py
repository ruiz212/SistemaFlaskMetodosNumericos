"""
grafica_nl.py
=============
Genera los puntos para graficar f(x) y las marcas de convergencia
de los métodos de ecuaciones no lineales.

Se importa desde app.py y se llama en la ruta /api/grafica_nl.
"""

import numpy as np
from metodos.utils import compilar_funciones


def generar_datos_grafica(ecuacion: str, metodo: str, resultados: list,
                          modo_angulo: str = 'rad') -> dict:
    """
    Genera los datos necesarios para graficar f(x) y los pasos
    de convergencia del método numérico seleccionado.

    Retorno
    -------
    dict con:
        - 'curva'   : {'x': [...], 'y': [...]}
        - 'raiz'    : float
        - 'pasos_x' : [...]
        - 'pasos_y' : [...]
        - 'metodo'  : str
    """
    # ── 1. Compilar la función ──────────────────────────────────────────────
    exito, msg, x_sym, expr_sim, _, f_eval, _ = compilar_funciones(ecuacion, modo_angulo)
    if not exito:
        return {"error": f"No se pudo compilar la ecuación: {msg}"}

    def f_safe(v):
        """Evalúa f(v) devolviendo None si hay cualquier error numérico."""
        try:
            val = f_eval(v)
            if val is None:
                return None
            fv = float(val)
            if np.isnan(fv) or np.isinf(fv):
                return None
            return fv
        except Exception:
            return None

    # ── 2. Extraer pasos de convergencia ────────────────────────────────────
    pasos_x = _extraer_pasos_x(metodo, resultados)

    if not pasos_x:
        return {"error": "No se encontraron datos de iteración para graficar."}

    raiz = pasos_x[-1]

    # ── 3. Calcular rango representativo de la curva ─────────────────────────
    #      Se explora un intervalo amplio y se recorta al dominio válido
    x_min, x_max = _calcular_rango_representativo(f_safe, raiz)

    # ── 4. Generar 600 puntos de la curva ────────────────────────────────────
    xs_all = np.linspace(x_min, x_max, 600)
    ys_raw = [f_safe(xi) for xi in xs_all]

    # Filtrar outliers extremos (asíntotas, discontinuidades)
    ys_validos = [y for y in ys_raw if y is not None]
    if not ys_validos:
        return {"error": "La función no produce valores reales en el rango de graficación."}

    # Límite de recorte: percentil 97 del valor absoluto × 2
    p97 = np.percentile(np.abs(ys_validos), 97) * 2 + 1e-9
    ys_clean = [
        y if (y is not None and abs(y) <= p97) else None
        for y in ys_raw
    ]

    curva_x = [round(float(xi), 8) for xi in xs_all]
    curva_y = [round(y, 8) if y is not None else None for y in ys_clean]

    # ── 5. Calcular f(x) en cada paso de iteración ──────────────────────────
    pasos_y = []
    for px in pasos_x:
        fy = f_safe(px)
        pasos_y.append(round(fy, 8) if fy is not None else 0.0)

    return {
        "curva":    {"x": curva_x, "y": curva_y},
        "raiz":     round(float(raiz), 8),
        "pasos_x":  [round(float(p), 8) for p in pasos_x],
        "pasos_y":  pasos_y,
        "metodo":   metodo,
    }


# ─── Rango representativo ─────────────────────────────────────────────────────

def _calcular_rango_representativo(f_safe, raiz: float,
                                   amplitud: float = 5.0,
                                   pasos: int = 200) -> tuple:
    """
    Determina un rango [x_min, x_max] que muestre la forma real de f(x).

    Estrategia:
    1. Parte de un intervalo candidato centrado en la raíz con amplitud 'amplitud'.
    2. Expande hacia la izquierda/derecha mientras haya puntos válidos,
       hasta un máximo de 5× la amplitud original.
    3. Recorta los extremos donde la función deje de ser evaluable (ej. ln(x<0)).
    """
    amp = max(abs(raiz) * 0.5, amplitud)   # nunca menor a 'amplitud'

    # Candidato inicial
    cand_min = raiz - amp
    cand_max = raiz + amp

    # Expandir hasta 5× si hay más dominio válido
    for factor in [1.5, 2.0, 3.0, 5.0]:
        nuevo_min = raiz - amp * factor
        nuevo_max = raiz + amp * factor
        if _hay_puntos_validos(f_safe, nuevo_min, cand_min, pasos // 4):
            cand_min = nuevo_min
        if _hay_puntos_validos(f_safe, cand_max, nuevo_max, pasos // 4):
            cand_max = nuevo_max

    # Recortar desde la izquierda hasta encontrar dominio válido
    xs_test = np.linspace(cand_min, cand_max, pasos)
    primer_valido = cand_min
    ultimo_valido = cand_max

    for xi in xs_test:
        if f_safe(xi) is not None:
            primer_valido = xi
            break

    for xi in reversed(xs_test):
        if f_safe(xi) is not None:
            ultimo_valido = xi
            break

    # Agregar un pequeño margen visual
    span = ultimo_valido - primer_valido
    margen = max(span * 0.05, 0.1)

    x_min = primer_valido + margen          # justo dentro del dominio
    x_max = ultimo_valido + margen

    # Seguridad: rango mínimo de 2 unidades
    if x_max - x_min < 2:
        cx = (x_min + x_max) / 2
        x_min, x_max = cx - 1, cx + 1

    return x_min, x_max


def _hay_puntos_validos(f_safe, x_desde, x_hasta, n: int) -> bool:
    """Devuelve True si al menos un punto en [x_desde, x_hasta] es evaluable."""
    if x_desde >= x_hasta:
        return False
    for xi in np.linspace(x_desde, x_hasta, n):
        if f_safe(xi) is not None:
            return True
    return False


# ─── Extracción de pasos de iteración ─────────────────────────────────────────

def _extraer_pasos_x(metodo: str, resultados: list) -> list:
    """
    Extrae la secuencia de aproximaciones x del resultado del método.
    Los valores pueden venir como strings formateados o como floats.
    """
    pasos = []

    def _to_float(v):
        if v is None:
            return None
        try:
            return float(str(v).replace('%', '').replace('---', '').strip() or 'nan')
        except (ValueError, TypeError):
            return None

    try:
        if metodo in ('Bisección', 'Regla Falsa'):
            for r in resultados:
                val = _to_float(r.get('c'))
                if val is not None and not np.isnan(val):
                    pasos.append(val)

        elif metodo == 'Newton-Raphson':
            for r in resultados:
                # Preferir cimas1 (ci+1), fallback a ci
                raw = r.get('cimas1') or r.get('ci')
                val = _to_float(raw)
                if val is not None and not np.isnan(val):
                    pasos.append(val)

        elif metodo == 'Secante':
            for r in resultados:
                val = _to_float(r.get('ci'))
                if val is not None and not np.isnan(val):
                    pasos.append(val)

        elif metodo == 'Punto fijo':
            for r in resultados:
                val = _to_float(r.get('ci'))
                if val is not None and not np.isnan(val):
                    pasos.append(val)

    except Exception:
        pass

    return pasos
