from flask import render_template, request, jsonify
from . import aplicacion_bp
from .clima_api import obtener_datos_clima
from .optimizacion import calcular_angulo_optimo, calcular_energia_total

@aplicacion_bp.route('/panel_solar')
def panel_solar():
    return render_template('aplicacion/panel_solar.html')

@aplicacion_bp.route('/api/simular', methods=['POST'])
def api_simular():
    data = request.json
    lat = float(data.get('lat', 0))
    lon = float(data.get('lon', 0))
    coef = float(data.get('coef', 0.45)) # Valor por defecto (panel genérico)
    
    # 1. Obtener datos de la API
    clima = obtener_datos_clima(lat, lon)
    if not clima.get('success'):
        return jsonify(clima)
        
    # 2. Calcular energía total y pérdida térmica (Integración Numérica)
    energia = calcular_energia_total(clima["datos_horarios"], coef)
    
    # 3. Calcular ángulo óptimo (Raíces de Ecuaciones - Newton-Raphson)
    max_rad = clima["max_radiacion"]
    optimizacion = calcular_angulo_optimo(lat, max_rad)
    
    if "error" in optimizacion:
        return jsonify({"success": False, "error": optimizacion["error"]})
        
    return jsonify({
        "success": True,
        "clima": clima["datos_horarios"],
        "curva_real": energia["curva_real"],
        "energia_ideal": energia["energia_ideal"],
        "energia_real": energia["energia_real"],
        "energia_perdida": energia["energia_perdida"],
        "angulo_optimo": optimizacion["angulo"],
        "max_radiacion": max_rad
    })

# Ruta IoT que un ESP32/Arduino leería
@aplicacion_bp.route('/api/iot/angulo_actual', methods=['GET'])
def iot_angulo():
    # En un sistema real, este ángulo vendría de una base de datos o variable global
    # que se actualiza con la simulación.
    # Simulamos retornar un valor por defecto para demostración IoT.
    lat = request.args.get('lat', default=0, type=float)
    lon = request.args.get('lon', default=0, type=float)
    clima = obtener_datos_clima(lat, lon)
    max_rad = clima.get("max_radiacion", 1000)
    opt = calcular_angulo_optimo(lat, max_rad)
    angulo = opt.get("angulo", 30.0) if "error" not in opt else 30.0
    
    return jsonify({"angulo_servo": angulo})
