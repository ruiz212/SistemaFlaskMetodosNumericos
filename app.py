from flask import Flask, render_template, request, jsonify
import numpy as np
from metodos.utils import compilar_funciones, evaluar_f, evaluar_df
from metodos.biseccion import biseccion
from metodos.regla_falsa import regla_falsa
from metodos.newton_raphson import newton_raphson
from metodos.secante import secante
from metodos.punto_fijo import punto_fijo
from metodos.muller import metodo_muller
from metodos.bairstow import metodo_bairstow
from metodos.horner_newton import metodo_horner_newton
from metodos.sistemas import resolver_sistema_no_lineal
from metodos.grafica_nl import generar_datos_grafica
from metodos.sistemas_lineales import (
    eliminacion_gaussiana, factorizacion_lu, 
    regla_de_cramer, gauss_jordan, matriz_inversa,
    metodo_jacobi, metodo_gauss_seidel,
    ordenar_matriz_dominante
)
from metodos.despejes import despejar_ecuacion

app = Flask(__name__)

# =========================================================================
# RUTAS DE VISTAS (PÁGINAS)
# =========================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/google63f1328f737677ff.html')
def google_verification():
    return "google-site-verification: google63f1328f737677ff.html"

@app.route('/no-lineales')
def no_lineales():
    return render_template('no_lineales.html')

@app.route('/polinomios')
def polinomios():
    return render_template('polinomios.html')

@app.route('/sistemas')
def sistemas():
    return render_template('sistemas.html')

@app.route('/sistemas-lineales')
def sistemas_lineales():
    return render_template('sistemas_lineales.html')

@app.route('/iterativos')
def iterativos():
    return render_template('iterativos.html')

@app.route('/interpolacion')
def interpolacion():
    return render_template('interpolacion.html')


# =========================================================================
# API: ECUACIONES NO LINEALES
# =========================================================================

@app.route('/api/calcular_nl', methods=['POST'])
def calcular_nl():
    data = request.json
    ecuacion = data.get('ecuacion', '').strip()
    metodo = data.get('metodo')
    tol_str = data.get('tol')
    modo_angulo = data.get('angulo', 'rad')
    cfg = data.get('cfg', {})
    
    if not ecuacion:
        return jsonify({'error': 'Ingresa una ecuación.'})
    
    try:
        tol = float(tol_str)
    except (ValueError, TypeError):
        return jsonify({'error': 'Tolerancia inválida.'})
        
    exito, msg, x_sym, expr_simbolica, derivada_simbolica, funcion_eval, derivada_eval = compilar_funciones(ecuacion, modo_angulo)
    if not exito:
        return jsonify({'error': f"Error en la sintaxis matemática: {msg}"})
        
    def f(v): return evaluar_f(v, expr_simbolica, x_sym, funcion_eval)
    def df(v): return evaluar_df(v, derivada_simbolica, x_sym, derivada_eval)

    try:
        if metodo == "Bisección":
            a = float(data.get('a'))
            b = float(data.get('b'))
            res = biseccion(a, b, tol, f, cfg)
        elif metodo == "Regla Falsa":
            a = float(data.get('a'))
            b = float(data.get('b'))
            res = regla_falsa(a, b, tol, f, cfg)
        elif metodo == "Newton-Raphson":
            ci = float(data.get('ci'))
            res = newton_raphson(ci, tol, f, df, cfg)
        elif metodo == "Secante":
            x0 = float(data.get('x0'))
            x1 = float(data.get('x1'))
            res = secante(x0, x1, tol, f, cfg)
        elif metodo == "Punto fijo":
            x0 = float(data.get('x0'))
            g_prima = df(x0)
            res = punto_fijo(x0, tol, f, data.get('force', False), g_prima, cfg)
            
        if "error" in res:
            return jsonify({'error': res["error"]})
        if "warning" in res:
            return jsonify({'warning': res["warning"]})
            
        return jsonify({'success': True, 'resultados': res["resultados"], 'mensaje': res["mensaje"], 'metodo': metodo})
    except ValueError as ve:
        return jsonify({'error': f"Error en los valores de entrada: {ve}"})
    except Exception as e:
        return jsonify({'error': f"Error inesperado: {str(e)}"})

@app.route('/api/despejar_punto_fijo', methods=['POST'])
def api_despejar_punto_fijo():
    data = request.json
    ecuacion = data.get('ecuacion', '').strip()
    x0_str = data.get('x0')
    
    if not ecuacion:
        return jsonify({'error': 'Ingresa una ecuación para despejar.'})
    
    x0 = None
    if x0_str:
        try:
            x0 = float(x0_str)
        except:
            pass
            
    res = despejar_ecuacion(ecuacion, x0)
    return jsonify(res)

@app.route('/api/grafica_nl', methods=['POST'])
def grafica_nl():
    data = request.json
    ecuacion = data.get('ecuacion', '').strip()
    metodo   = data.get('metodo', '')
    resultados = data.get('resultados', [])
    modo_angulo = data.get('angulo', 'rad')

    if not ecuacion:
        return jsonify({'error': 'Ingresa una ecuación para graficar.'})
    
    try:
        datos = generar_datos_grafica(ecuacion, metodo, resultados, modo_angulo)
        if 'error' in datos:
            return jsonify({'error': datos['error']})
        return jsonify({'success': True, 'datos': datos})
    except Exception as e:
        return jsonify({'error': str(e)})

# =========================================================================
# API: POLINOMIOS (RAÍCES COMPLEJAS)
# =========================================================================

@app.route('/api/calcular_pol', methods=['POST'])
def calcular_pol():
    data = request.json
    metodo = data.get('metodo')
    a_input = data.get('coeficientes', [])
    tol_str = data.get('tol', '')
    cfg = data.get('cfg', {})
    
    try:
        tol_porcentaje = float(tol_str)
    except ValueError:
        return jsonify({'error': 'Tolerancia inválida.'})
    
    try:
        if metodo == "Müller":
            if not a_input:
                return jsonify({'error': 'Faltan coeficientes.'})
            a_input = [float(x) for x in a_input]
            # Coeficientes en python suelen ir de a0 a an para evaluar facil, 
            # pero el usuario los ingresa de an a a0. main.js los manda en orden de an a a0.
            # metodo_muller espera de a0 a an si usa enumerate(a_coefs).
            a_input.reverse() 

            x0 = float(data.get('x0'))
            x1 = float(data.get('x1'))
            x2 = float(data.get('x2'))
            res = metodo_muller(x0=x0, x1=x1, x2=x2, tol_porcentaje=tol_porcentaje, a_coefs=a_input, cfg=cfg)
        else:
            if not a_input:
                return jsonify({'error': 'Faltan coeficientes.'})
            a_input = [float(x) for x in a_input]
            
            if metodo == "Bairstow":
                r0 = data.get('r0')
                s0 = data.get('s0')
                res = metodo_bairstow(a_input, tol_porcentaje, r0, s0, cfg)
            elif metodo == "Horner-Newton":
                r0_str = data.get('r0')
                try:
                    r = complex(r0_str) if 'j' in r0_str else float(r0_str)
                except ValueError:
                    return jsonify({'error': 'Valor inicial inválido.'})
                res = metodo_horner_newton(a_input, r, tol_porcentaje, cfg)
            
        if "error" in res:
            return jsonify({'error': res["error"], 'consola': "\n".join(res.get("consola", []))})
            
        return jsonify({
            'success': True, 
            'resultados': res["resultados"], 
            'consola': "\n".join(res["consola"]), 
            'metodo': metodo, 
            'encabezados': res.get('encabezados', []),
            'r_init': res.get('r_init'),
            's_init': res.get('s_init')
        })
    except Exception as e:
        return jsonify({'error': f"Error inesperado: {str(e)}"})

# =========================================================================
# API: SISTEMAS NO LINEALES
# =========================================================================

@app.route('/api/calcular_sis', methods=['POST'])
def calcular_sis():
    print("[DEBUG] Petición recibida en /api/calcular_sis")
    data = request.json
    n = int(data.get('n', 2))
    funciones_txt = data.get('funciones', [])
    valores_x = data.get('x0', [])
    tol_str = data.get('tol', '')
    iter_str = data.get('iter', '')
    modo_angulo = data.get('angulo', 'rad')
    
    if not tol_str or not iter_str:
        return jsonify({'error': 'Llene Tolerancia y Máximo de Iteraciones.'})
        
    try:
        tol = float(tol_str)
        max_iter = int(iter_str)
    except ValueError:
        return jsonify({'error': 'Tolerancia o Iteraciones inválidas.'})
        
    try:
        res = resolver_sistema_no_lineal(n, funciones_txt, valores_x, tol, max_iter, modo_angulo)
        if "error" in res:
            return jsonify({'error': res["error"], 'consola': "\n".join(res.get("consola", []))})
            
        return jsonify({
            'success': True,
            'resultados': res["resultados"],
            'headers':    res["headers"],
            'consola':    "\n".join(res["consola"]),
            'raiz':       res.get("raiz", []),
            'var_names':  res.get("var_names", [])
        })

    except ValueError:
        return jsonify({'error': 'Valores iniciales inválidos.'})
    except Exception as e:
        return jsonify({'error': f"Error inesperado: {str(e)}"})

@app.route('/configuracion')
def configuracion():
    return render_template('configuracion.html')

@app.route('/api/calcular_sis_lin', methods=['POST'])
def calcular_sis_lin():
    data = request.json
    metodo = data.get('metodo')
    A = np.array(data.get('A'))
    b = np.array(data.get('b'))
    cfg = data.get('cfg', {})
    
    if metodo == "Eliminación Gaussiana":
        res = eliminacion_gaussiana(A, b)
    elif metodo == "Factorización LU":
        res = factorizacion_lu(A, b)
    elif metodo == "Regla de Cramer":
        res = regla_de_cramer(A, b)
    elif metodo == "Gauss-Jordan":
        res = gauss_jordan(A, b)
    elif metodo == "Matriz Inversa":
        res = matriz_inversa(A, b)
    elif metodo == "Jacobi":
        x0 = data.get('x0', [0.0]*len(b))
        tol = float(data.get('tol', 0.001))
        max_iter = int(data.get('max_iter', 100))
        res = metodo_jacobi(A, b, x0, tol, max_iter, cfg)
    elif metodo == "Gauss-Seidel":
        x0 = data.get('x0', [0.0]*len(b))
        tol = float(data.get('tol', 0.001))
        max_iter = int(data.get('max_iter', 100))
        res = metodo_gauss_seidel(A, b, x0, tol, max_iter, cfg)
    else:
        return jsonify({'error': 'Método no soportado'})
        
    return jsonify({'success': True, 'resultado': res})

@app.route('/api/ordenar_matriz', methods=['POST'])
def api_ordenar_matriz():
    data = request.json
    A = np.array(data.get('A'))
    b = np.array(data.get('b'))
    
    res = ordenar_matriz_dominante(A, b)
    if "error" in res:
        return jsonify({'error': res["error"]})
        
    return jsonify({'success': True, 'resultado': res})

@app.route('/api/grafica_sis_3d', methods=['POST'])
def grafica_sis_3d():
    """
    Genera datos de visualización 3D para sistemas no lineales.
    - n=2 → mode='2d': superficies f(x,y)
    - n>=3 → mode='3d': isosuperficies f(x,y,z)=0 (volumétrico)
    Evaluación 100% NumPy vectorizado — sin SymPy, sin latencia.
    """
    import math, re

    data       = request.json
    funciones_txt = data.get('funciones', [])
    x_sol      = data.get('x_sol', [])
    n          = int(data.get('n', 2))
    var_x_req  = data.get('var_x')   # nombre eje X (n>3)
    var_y_req  = data.get('var_y')   # nombre eje Y (n>3)
    var_z_req  = data.get('var_z')   # nombre eje Z (n>3)
    fixed_vars = data.get('fixed_vars', {})   # {nombre: valor} para n>3
    var_names_hint = data.get('var_names', [])

    if len(funciones_txt) < 2:
        return jsonify({'error': 'Se requieren al menos 2 ecuaciones.'})

    # ── Normalizar expresiones ──────────────────────────────────────────────
    def normalizar(expr):
        expr = expr.replace('^', '**')
        expr = re.sub(r'\bsen\b', 'sin', expr)
        expr = re.sub(r'\btg\b',  'tan', expr)
        expr = re.sub(r'\bln\b',  'log', expr)
        expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)
        return expr

    # ── Detectar variables ──────────────────────────────────────────────────
    FUNCIONES_CONOCIDAS = {'sin','cos','tan','sen','tg','ln','log','exp','sqrt',
                           'abs','pi','e','asin','acos','atan','sinh','cosh','tanh',
                           'floor','ceil','round'}
    todas_vars = set()
    for txt in funciones_txt:
        for tok in re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', txt):
            if tok not in FUNCIONES_CONOCIDAS and len(tok) <= 4:
                todas_vars.add(tok)
    vars_ordenadas = sorted(todas_vars)

    # Determinar ejes
    vx = var_x_req or (vars_ordenadas[0] if len(vars_ordenadas) > 0 else 'x')
    vy = var_y_req or (vars_ordenadas[1] if len(vars_ordenadas) > 1 else 'y')
    vz = var_z_req or (vars_ordenadas[2] if len(vars_ordenadas) > 2 else 'z')

    # ── Contexto NumPy base ─────────────────────────────────────────────────
    NP_CTX = {
        'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
        'exp': np.exp, 'log': np.log, 'sqrt': np.sqrt,
        'abs': np.abs, 'pi': np.pi,   'e':   np.e,
        'asin': np.arcsin, 'acos': np.arccos, 'atan': np.arctan,
        'sinh': np.sinh,   'cosh': np.cosh,   'tanh': np.tanh,
        'floor': np.floor, 'ceil': np.ceil
    }
    # Añadir variables fijadas (n>3)
    for k, v in fixed_vars.items():
        try:
            NP_CTX[k] = float(v)
        except Exception:
            pass

    # ── Rango centrado en solución ──────────────────────────────────────────
    sol_map = {}
    if x_sol and vars_ordenadas:
        for i, vn in enumerate(vars_ordenadas):
            if i < len(x_sol):
                sol_map[vn] = float(x_sol[i])

    def centro(vname, default=0.0):
        return sol_map.get(vname, default)

    delta = 5.0

    # ══════════════════════════════════════════════════════════════════════════
    # MODO 2D — n=2: superficies f(x,y) sobre malla 2D
    # ══════════════════════════════════════════════════════════════════════════
    if n <= 2:
        GRID = 45
        cx = centro(vx); cy = centro(vy)
        x_lin = np.linspace(cx - delta, cx + delta, GRID)
        y_lin = np.linspace(cy - delta, cy + delta, GRID)
        Xm, Ym = np.meshgrid(x_lin, y_lin)

        res_z = []
        for txt in funciones_txt[:2]:
            expr_clean = normalizar(txt)
            ctx = dict(NP_CTX)
            ctx[vx] = Xm; ctx[vy] = Ym
            try:
                Z = eval(expr_clean, {"__builtins__": {}}, ctx)  # noqa: S307
                if np.isscalar(Z):
                    Z = np.full(Xm.shape, float(Z))
                else:
                    Z = np.asarray(Z, dtype=complex)
                    if np.iscomplexobj(Z):
                        Z = Z.real
                    Z = Z.astype(float)
                Z = np.nan_to_num(Z, nan=0.0, posinf=1e3, neginf=-1e3)
            except Exception as ex:
                print(f"[3D-2D ERROR] {ex}")
                Z = np.zeros_like(Xm)
            res_z.append(Z.tolist())

        return jsonify({
            'success': True, 'mode': '2d',
            'X': x_lin.tolist(), 'Y': y_lin.tolist(), 'Z': res_z,
            'simbolos': [vx, vy], 'var_names': vars_ordenadas
        })

    # ══════════════════════════════════════════════════════════════════════════
    # MODO 3D — n>=3: isosuperficies f(x,y,z)=0 sobre malla 3D
    # ══════════════════════════════════════════════════════════════════════════
    GRID3 = 22  # 22^3 = 10648 pts — rápido y suficientemente denso
    cx = centro(vx); cy = centro(vy); cz = centro(vz)

    x_lin = np.linspace(cx - delta, cx + delta, GRID3)
    y_lin = np.linspace(cy - delta, cy + delta, GRID3)
    z_lin = np.linspace(cz - delta, cz + delta, GRID3)

    # Malla 3D indexada con 'ij' para consistencia con Plotly
    Xg, Yg, Zg = np.meshgrid(x_lin, y_lin, z_lin, indexing='ij')

    x_flat = Xg.flatten().tolist()
    y_flat = Yg.flatten().tolist()
    z_flat = Zg.flatten().tolist()

    values_list = []
    # Para n=3 graficamos las 3 funciones; para n>3 solo f1 y f2
    n_funcs = min(n, 3)
    for txt in funciones_txt[:n_funcs]:
        expr_clean = normalizar(txt)
        ctx = dict(NP_CTX)
        ctx[vx] = Xg; ctx[vy] = Yg; ctx[vz] = Zg
        try:
            V = eval(expr_clean, {"__builtins__": {}}, ctx)  # noqa: S307
            if np.isscalar(V):
                V = np.full(Xg.shape, float(V))
            else:
                V = np.asarray(V, dtype=complex)
                if np.iscomplexobj(V):
                    V = V.real
                V = V.astype(float)
            V = np.nan_to_num(V, nan=0.0, posinf=1e6, neginf=-1e6)
        except Exception as ex:
            print(f"[3D-ISO ERROR] {ex}")
            V = np.zeros_like(Xg)
        values_list.append(V.flatten().tolist())

    return jsonify({
        'success': True, 'mode': '3d',
        'x_flat': x_flat, 'y_flat': y_flat, 'z_flat': z_flat,
        'x_lin': x_lin.tolist(), 'y_lin': y_lin.tolist(), 'z_lin': z_lin.tolist(),
        'values': values_list,
        'simbolos': [vx, vy, vz],
        'var_names': vars_ordenadas
    })



@app.route('/api/calcular_interpolacion', methods=['POST'])
def calcular_interpolacion():
    data = request.json
    x_puntos = np.array(data.get('x'), dtype=float)
    y_puntos = np.array(data.get('y'), dtype=float)
    metodo = data.get('metodo')
    cfg = data.get('cfg', {})
    
    if metodo == "Diferencias Divididas":
        from metodos.interpolacion_newton import NewtonDividedDifferences
        try:
            # Tolerancia por defecto o desde el frontend si existiera
            tolerancia = float(data.get('tol', 0.001))
            interpolador = NewtonDividedDifferences(x_puntos, y_puntos, tolerancia=tolerancia, cfg=cfg)
            interpolador.calcular_polinomio_optimo()
            
            coefs = interpolador.coeficientes.tolist() if hasattr(interpolador.coeficientes, 'tolist') else interpolador.coeficientes
            ecuacion = interpolador.obtener_ecuacion_string()
            grado = interpolador.grado_optimo
            
            # Formatear la tabla para devolverla
            tabla_serializable = []
            if interpolador.tabla is not None:
                for row in interpolador.tabla:
                    tabla_serializable.append([float(val) if not np.isnan(val) else "" for val in row])
                    
            return jsonify({
                'success': True, 
                'coefs': coefs,
                'ecuacion': ecuacion,
                'polinomios_pasos': interpolador.obtener_polinomios_pasos(),
                'errores_pasos': interpolador.errores_pasos,
                'razon_detencion': interpolador.razon_detencion,
                'grado': grado,
                'tabla': tabla_serializable,
                'warnings': interpolador.warnings
            })
        except Exception as e:
            return jsonify({'error': str(e)})
            
    return jsonify({'error': 'Método no soportado'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
