from flask import Flask, render_template, request, jsonify
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

app = Flask(__name__)

# =========================================================================
# RUTAS DE VISTAS (PÁGINAS)
# =========================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/no-lineales')
def no_lineales():
    return render_template('no_lineales.html')

@app.route('/polinomios')
def polinomios():
    return render_template('polinomios.html')

@app.route('/sistemas')
def sistemas():
    return render_template('sistemas.html')

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
            res = biseccion(a, b, tol, f)
        elif metodo == "Regla Falsa":
            a = float(data.get('a'))
            b = float(data.get('b'))
            res = regla_falsa(a, b, tol, f)
        elif metodo == "Newton-Raphson":
            ci = float(data.get('ci'))
            res = newton_raphson(ci, tol, f, df)

        elif metodo == "Secante":
            x0 = float(data.get('x0'))
            x1 = float(data.get('x1'))
            res = secante(x0, x1, tol, f)
            
        elif metodo == "Punto fijo":
            x0 = float(data.get('x0'))
            g_prima = df(x0)
            res = punto_fijo(x0, tol, f, data.get('force', False), g_prima)
            
        if "error" in res:
            return jsonify({'error': res["error"]})
        if "warning" in res:
            return jsonify({'warning': res["warning"]})
            
        return jsonify({'success': True, 'resultados': res["resultados"], 'mensaje': res["mensaje"], 'metodo': metodo})
    except ValueError as ve:
        return jsonify({'error': f"Error en los valores de entrada: {ve}"})
    except Exception as e:
        return jsonify({'error': f"Error inesperado: {str(e)}"})

# =========================================================================
# API: POLINOMIOS (RAÍCES COMPLEJAS)
# =========================================================================

@app.route('/api/calcular_pol', methods=['POST'])
def calcular_pol():
    data = request.json
    metodo = data.get('metodo')
    a_input = data.get('coeficientes', [])
    tol_str = data.get('tol', '')
    
    if not a_input:
        return jsonify({'error': 'Faltan coeficientes.'})
        
    try:
        tol_porcentaje = float(tol_str)
        a_input = [float(x) for x in a_input]
    except ValueError:
        return jsonify({'error': 'Valores o tolerancia inválidos.'})
        
    try:
        if metodo == "Müller":
            x0 = float(data.get('x0'))
            x1 = float(data.get('x1'))
            x2 = float(data.get('x2'))
            res = metodo_muller(a_input[::-1], x0, x1, x2, tol_porcentaje)
                    
        elif metodo == "Bairstow":
            r0 = data.get('r0')
            s0 = data.get('s0')
            res = metodo_bairstow(a_input, tol_porcentaje, r0, s0)

        elif metodo == "Horner-Newton":
            r0_str = data.get('r0')
            try:
                r = complex(r0_str) if 'j' in r0_str else float(r0_str)
            except ValueError:
                return jsonify({'error': 'Valor inicial inválido.'})
            res = metodo_horner_newton(a_input, r, tol_porcentaje)
            
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
            
        return jsonify({'success': True, 'resultados': res["resultados"], 'headers': res["headers"], 'consola': "\n".join(res["consola"])})
    except ValueError:
        return jsonify({'error': 'Valores iniciales inválidos.'})
    except Exception as e:
        return jsonify({'error': f"Error inesperado: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
