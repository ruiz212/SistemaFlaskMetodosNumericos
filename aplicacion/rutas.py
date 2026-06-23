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
        "energia_real_romberg": energia.get("energia_real_romberg", 0),
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

# ==========================================
# RUTAS DRONES AUTÓNOMOS (AEROESPACIAL)
# ==========================================
from .drones import generar_terreno_ciudad, generar_terreno_corredor, calcular_ruta_a_star, calcular_trayectoria_spline, generar_telemetria, latlon_to_xy, haversine

@aplicacion_bp.route('/drones')
def drones():
    return render_template('aplicacion/drones.html')

@aplicacion_bp.route('/api/drones/simular', methods=['POST'])
def api_drones_simular():
    data = request.json
    start_gps = data.get('start', [0, 0]) # [lat, lon]
    end_gps = data.get('end', [0, 0]) # [lat, lon]
    
    min_lat = min(start_gps[0], end_gps[0])
    max_lat = max(start_gps[0], end_gps[0])
    min_lon = min(start_gps[1], end_gps[1])
    max_lon = max(start_gps[1], end_gps[1])
    
    # Agregar margen del 20% para el cálculo (igual que en drones.py)
    margen_lat = (max_lat - min_lat) * 0.2
    margen_lon = (max_lon - min_lon) * 0.2
    min_lat_q = min_lat - margen_lat
    min_lon_q = min_lon - margen_lon
    
    # Convertir GPS a XY locales para el simulador 3D
    sx, sy = latlon_to_xy(start_gps[0], start_gps[1], min_lat_q, min_lon_q)
    ex, ey = latlon_to_xy(end_gps[0], end_gps[1], min_lat_q, min_lon_q)
    start_xy = [sx, sy]
    end_xy = [ex, ey]
    
    # 1. Generar Terreno Real (OSM) — SIEMPRE datos reales
    dist_km = haversine(start_gps[0], start_gps[1], end_gps[0], end_gps[1]) / 1000.0
    if dist_km > 2.0:
        edificios, calles, manzanas, size = generar_terreno_corredor(min_lat, max_lat, min_lon, max_lon, sx, sy, ex, ey)
    else:
        edificios, calles, manzanas, size = generar_terreno_ciudad(min_lat, max_lat, min_lon, max_lon)
    
    # 2. Pathfinding (Evadir obstáculos)
    ruta_cruda = calcular_ruta_a_star(start_xy, end_xy, edificios)
    
    # 3. Métodos Numéricos: Interpolación por Splines para curva de vuelo suave
    ruta_suave = calcular_trayectoria_spline(ruta_cruda)
    
    # 4. Métodos Numéricos: Integración de Simpson para telemetría inercial
    telemetria = generar_telemetria(ruta_suave)
    
    return jsonify({
        "success": True,
        "terreno": {
            "edificios": edificios, 
            "calles": calles,
            "manzanas": manzanas,
            "size": size
        },
        "ruta_cruda": ruta_cruda,
        "ruta_suave": ruta_suave,
        "telemetria": telemetria
    })
