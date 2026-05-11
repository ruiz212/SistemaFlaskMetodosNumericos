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
from metodos.sistemas_lineales import eliminacion_gaussiana, factorizacion_lu

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

@app.route('/sistemas-lineales')
def sistemas_lineales():
    return render_template('sistemas_lineales.html')

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
            res = metodo_muller(x0=x0, x1=x1, x2=x2, tol_porcentaje=tol_porcentaje, a_coefs=a_input)
        else:
            if not a_input:
                return jsonify({'error': 'Faltan coeficientes.'})
            a_input = [float(x) for x in a_input]
            
            if metodo == "Bairstow":
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

@app.route('/api/calcular_sis_lin', methods=['POST'])
def calcular_sis_lin():
    data = request.json
    metodo = data.get('metodo')
    A = np.array(data.get('A'))
    b = np.array(data.get('b'))
    
    if metodo == "Eliminación Gaussiana":
        res = eliminacion_gaussiana(A, b)
    elif metodo == "Factorización LU":
        res = factorizacion_lu(A, b)
    else:
        return jsonify({'error': 'Método no soportado'})
        
    return jsonify({'success': True, 'resultado': res})

@app.route('/api/grafica_sis_3d', methods=['POST'])
def grafica_sis_3d():
    data = request.json
    funciones = data.get('funciones', [])
    if len(funciones) != 2:
        return jsonify({'error': 'Solo disponible para 2 variables'})
    
    # Rango de graficación
    x = np.linspace(-5, 5, 40)
    y = np.linspace(-5, 5, 40)
    X, Y = np.meshgrid(x, y)
    
    res = []
    for f_text in funciones:
        exito, _, _, expr, _, f_eval, _ = compilar_funciones(f_text)
        if not exito: return jsonify({'error': f'Error en {f_text}'})
        
        # Evaluar en malla
        Z = np.zeros(X.shape)
        for i in range(len(x)):
            for j in range(len(y)):
                # Newton Multivariable usa x1, x2...
                # Pero compilar_funciones asume 'x'
                # Necesitamos un helper para sistemas
                Z[j, i] = float(expr.subs({'x1': x[i], 'x2': y[j]}).evalf())
        res.append(Z.tolist())
        
    return jsonify({'success': True, 'X': x.tolist(), 'Y': y.tolist(), 'Z': res})

@app.route('/api/calcular_interpolacion', methods=['POST'])
def calcular_interpolacion():
    data = request.json
    x_puntos = np.array(data.get('x'), dtype=float)
    y_puntos = np.array(data.get('y'), dtype=float)
    metodo = data.get('metodo')
    
    from metodos.interpolacion import diferencias_divididas
    
    if metodo == "Diferencias Divididas":
        coefs, _ = diferencias_divididas(x_puntos, y_puntos)
        return jsonify({'success': True, 'coefs': coefs})
    
    return jsonify({'error': 'Método no soportado'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
