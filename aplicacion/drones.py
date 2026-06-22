import math
import numpy as np
import random
from metodos.interpolacion_splines import CubicSplinesInterpolator

import requests

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000 # Radio de la Tierra en metros
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2.0)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda/2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def latlon_to_xy(lat, lon, min_lat, min_lon):
    x = haversine(min_lat, min_lon, min_lat, lon)
    y = haversine(min_lat, min_lon, lat, min_lon)
    return x, y

def _generar_mock(area_size):
    area_size = max(area_size, 1000)
    edificios = []
    
    # Crear un grid organizado tipo "Manzanas de Ciudad"
    block_size = 80
    street_width = 30
    
    # Rango de coordenadas seguras
    start = 100
    end = int(area_size - 100)
    
    # Generar bloques
    for x in range(start, end, block_size + street_width):
        for y in range(start, end, block_size + street_width):
            # Posibilidad del 80% de haber un edificio en esta manzana
            if random.random() < 0.8:
                # Variabilidad dentro del bloque para que no todos sean iguales
                w = round(random.uniform(block_size * 0.5, block_size * 0.9), 2)
                d = round(random.uniform(block_size * 0.5, block_size * 0.9), 2)
                
                # Crear edificios altos y bajos (rascacielos en el centro)
                dist_to_center = math.hypot(x - area_size/2, y - area_size/2)
                max_h = 200 if dist_to_center < 300 else 80
                h = round(random.uniform(30, max_h), 2)
                
                cx = x + block_size/2
                cy = y + block_size/2
                puntos = [
                    {"x": cx - w/2, "y": cy - d/2},
                    {"x": cx + w/2, "y": cy - d/2},
                    {"x": cx + w/2, "y": cy + d/2},
                    {"x": cx - w/2, "y": cy + d/2}
                ]
                
                edificios.append({
                    "points": puntos,
                    "cx": cx,
                    "cy": cy,
                    "h": h,
                    "zone": "downtown" if max_h == 200 else "residential"
                })
                
    return edificios, area_size

def _query_osm_buildings_and_roads(min_lat, min_lon, max_lat, max_lon, ref_lat, ref_lon, timeout=15):
    """
    Consulta Overpass API para obtener polígonos de edificios y trayectorias de calles reales.
    Retorna (edificios, calles) con su geometría completa en coordenadas locales (x, y).
    """
    query = f"""
    [out:json][timeout:{timeout}];
    (
      way["building"]({min_lat},{min_lon},{max_lat},{max_lon});
      way["highway"~"^(motorway|trunk|primary|secondary|tertiary|residential|unclassified)$"]({min_lat},{min_lon},{max_lat},{max_lon});
    );
    out geom;
    """
    
    edificios = []
    calles = []
    
    try:
        headers = {"User-Agent": "Aero-AI-Drone-Simulation/1.0"}
        response = requests.post(
            "https://overpass-api.de/api/interpreter", 
            data={'data': query}, headers=headers, timeout=timeout
        )
        
        if response.status_code != 200:
            print(f"OSM API Error {response.status_code}: {response.text[:200]}")
            return edificios, calles
            
        data = response.json()
        
        for element in data.get("elements", []):
            tags = element.get("tags", {})
            geom = element.get("geometry", [])
            if not geom or len(geom) < 2:
                continue
                
            # Convertir geometría a coordenadas locales XY
            puntos = []
            sum_x, sum_y = 0, 0
            for pt in geom:
                x, y = latlon_to_xy(pt["lat"], pt["lon"], ref_lat, ref_lon)
                puntos.append({"x": round(x, 2), "y": round(y, 2)})
                sum_x += x
                sum_y += y
            
            centro_x = round(sum_x / len(geom), 2)
            centro_y = round(sum_y / len(geom), 2)
            
            # === EDIFICIOS ===
            if "building" in tags:
                # Altura real desde tags o estimada
                altura = 12
                if "height" in tags:
                    try:
                        h_str = tags["height"].replace("m", "").replace(",", ".").strip()
                        altura = float(h_str)
                    except: pass
                elif "building:levels" in tags:
                    try:
                        levels = float(tags["building:levels"])
                        altura = levels * 3.2
                    except: pass
                else:
                    btype = tags.get("building", "yes")
                    if btype in ("house", "detached"): altura = random.uniform(6, 10)
                    elif btype in ("apartments", "residential"): altura = random.uniform(12, 25)
                    elif btype in ("commercial", "office"): altura = random.uniform(15, 40)
                    elif btype in ("industrial", "warehouse"): altura = random.uniform(8, 15)
                    else: altura = random.uniform(8, 20)
                
                zone = "residential"
                btype = tags.get("building", "yes")
                if btype in ("commercial", "office", "retail"): zone = "commercial"
                elif altura > 40: zone = "downtown"
                
                edificios.append({
                    "points": puntos,
                    "cx": centro_x,
                    "cy": centro_y,
                    "h": round(altura, 2),
                    "zone": zone
                })
            
            # === CALLES ===
            elif "highway" in tags:
                highway_type = tags.get("highway", "residential")
                if highway_type in ("motorway", "trunk"):
                    width = 24
                    is_avenue = True
                elif highway_type in ("primary", "secondary"):
                    width = 18
                    is_avenue = True
                elif highway_type == "tertiary":
                    width = 14
                    is_avenue = False
                else:
                    width = 10
                    is_avenue = False
                
                calles.append({
                    "points": puntos,
                    "width": width,
                    "is_avenue": is_avenue
                })
    
    except Exception as e:
        print(f"Error consultando OSM: {e}")
    
    return edificios, calles


def generar_terreno_ciudad(min_lat, max_lat, min_lon, max_lon, num_edificios=30):
    """
    Usa Overpass API para obtener edificios Y calles reales.
    Si falla o no hay datos, retorna un generador por defecto.
    """
    width_m = haversine(min_lat, min_lon, min_lat, max_lon)
    height_m = haversine(min_lat, min_lon, max_lat, min_lon)
    area_size = max(width_m, height_m)
    
    margen_lat = (max_lat - min_lat) * 0.2
    margen_lon = (max_lon - min_lon) * 0.2
    min_lat_q = min_lat - margen_lat
    max_lat_q = max_lat + margen_lat
    min_lon_q = min_lon - margen_lon
    max_lon_q = max_lon + margen_lon
    
    edificios, calles = _query_osm_buildings_and_roads(
        min_lat_q, min_lon_q, max_lat_q, max_lon_q,
        min_lat_q, min_lon_q
    )

    if not edificios:
        mock_ed, mock_size = _generar_mock(width_m)
        return mock_ed, [], [], mock_size
        
    final_size = area_size + (haversine(min_lat_q, min_lon_q, min_lat_q, min_lon) * 2)
    return edificios, calles, [], final_size


def generar_terreno_corredor(min_lat, max_lat, min_lon, max_lon, sx, sy, ex, ey):
    """
    Para distancias largas: consulta OSM en segmentos a lo largo de la ruta
    para obtener edificios y calles REALES del corredor de vuelo.
    Si OSM falla, genera un fallback procedural.
    """
    width_m = haversine(min_lat, min_lon, min_lat, max_lon)
    height_m = haversine(min_lat, min_lon, max_lat, min_lon)
    area_size = max(width_m, height_m)
    
    # Coordenadas GPS del inicio y fin
    start_lat = min(min_lat, max_lat)
    start_lon = min(min_lon, max_lon)
    
    dist_m = math.hypot(ex - sx, ey - sy)
    
    # Dividir la ruta en segmentos de ~1.5 km para consultar OSM
    segment_length_m = 1500
    num_segments = max(1, min(8, int(dist_m / segment_length_m)))  # máximo 8 consultas
    
    all_edificios = []
    all_calles = []
    
    # El margen del corredor en grados (~0.004 grados ≈ 450 metros)
    corridor_deg = 0.004
    
    for seg in range(num_segments):
        t0 = seg / num_segments
        t1 = (seg + 1) / num_segments
        
        # Punto medio del segmento en GPS
        mid_t = (t0 + t1) / 2
        seg_lat = min_lat + (max_lat - min_lat) * mid_t
        seg_lon = min_lon + (max_lon - min_lon) * mid_t
        
        # Punto inicio y fin del segmento en GPS
        seg_min_lat = min_lat + (max_lat - min_lat) * t0 - corridor_deg
        seg_max_lat = min_lat + (max_lat - min_lat) * t1 + corridor_deg
        seg_min_lon = min_lon + (max_lon - min_lon) * t0 - corridor_deg
        seg_max_lon = min_lon + (max_lon - min_lon) * t1 + corridor_deg
        
        # Asegurar orden correcto
        if seg_min_lat > seg_max_lat:
            seg_min_lat, seg_max_lat = seg_max_lat, seg_min_lat
        if seg_min_lon > seg_max_lon:
            seg_min_lon, seg_max_lon = seg_max_lon, seg_min_lon
        
        # Referencia global (usamos el mínimo de todo el corredor para coordenadas consistentes)
        ref_lat = min_lat - (max_lat - min_lat) * 0.2
        ref_lon = min_lon - (max_lon - min_lon) * 0.2
        
        print(f"  [OSM] Consultando segmento {seg+1}/{num_segments}...")
        edificios_seg, calles_seg = _query_osm_buildings_and_roads(
            seg_min_lat, seg_min_lon, seg_max_lat, seg_max_lon,
            ref_lat, ref_lon,
            timeout=12
        )
        
        all_edificios.extend(edificios_seg)
        all_calles.extend(calles_seg)
        
        # Limitar para no saturar el navegador
        if len(all_edificios) > 1200:
            all_edificios = all_edificios[:1200]
            break
    
    print(f"  [OSM] Total: {len(all_edificios)} edificios reales, {len(all_calles)} calles reales")
    
    # Si no se obtuvieron datos reales, generar fallback procedural
    if not all_edificios:
        print("  [OSM] Sin datos reales, generando ciudad procedural de respaldo...")
        return _generar_corredor_fallback(sx, sy, ex, ey, area_size)
    
    return all_edificios, all_calles, [], area_size


def _generar_corredor_fallback(sx, sy, ex, ey, area_size):
    """Fallback procedural si OSM no devuelve datos."""
    edificios = []
    block_w = 100
    block_d = 80
    street_w = 18
    step_x = block_w + street_w
    step_y = block_d + street_w
    
    dx = ex - sx
    dy = ey - sy
    dist = math.hypot(dx, dy)
    if dist == 0: dist = 1
    ux = dx / dist
    uy = dy / dist
    px_dir = -uy
    py_dir = ux
    
    num_along = int(dist / step_x) + 4
    num_across = 6
    
    for i in range(-2, num_along + 2):
        for j in range(-num_across // 2, num_across // 2 + 1):
            bx = sx + ux * (i * step_x) + px_dir * (j * step_y)
            by = sy + uy * (i * step_x) + py_dir * (j * step_y)
            
            num_b = random.randint(1, 3)
            for _ in range(num_b):
                if len(edificios) >= 600:
                    return edificios, [], [], area_size
                lx = random.uniform(-35, 35)
                ly = random.uniform(-25, 25)
                w = round(random.uniform(12, 35), 2)
                d = round(random.uniform(10, 30), 2)
                h = round(random.uniform(8, 50), 2)
                
                cx, cy = round(bx + lx, 2), round(by + ly, 2)
                puntos = [
                    {"x": cx - w/2, "y": cy - d/2},
                    {"x": cx + w/2, "y": cy - d/2},
                    {"x": cx + w/2, "y": cy + d/2},
                    {"x": cx - w/2, "y": cy + d/2}
                ]
                
                edificios.append({
                    "points": puntos,
                    "cx": cx, "cy": cy,
                    "h": h, "zone": "residential"
                })
    
    return edificios, [], [], area_size

def _hay_colision(px, py, edificios, margen=20):
    for ed in edificios:
        # Si tiene puntos geográficos, calculamos el bounding box
        if "points" in ed:
            pts = ed["points"]
            xs = [p["x"] for p in pts]
            ys = [p["y"] for p in pts]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            if (min_x - margen) < px < (max_x + margen) and \
               (min_y - margen) < py < (max_y + margen):
                return True
        else:
            # Fallback por si acaso algún generador viejo sigue mandando w,d
            ex, ey, ew, ed_d = ed.get("x", 0), ed.get("y", 0), ed.get("w", 0), ed.get("d", 0)
            if (ex - ew/2 - margen) < px < (ex + ew/2 + margen) and \
               (ey - ed_d/2 - margen) < py < (ey + ed_d/2 + margen):
                return True
    return False

def calcular_ruta_a_star(start, end, edificios, grid_size=1000, step=50):
    """
    Simulación simplificada de Pathfinding.
    Genera waypoints crudos esquivando edificios.
    Retorna una lista de puntos (x, y, z).
    """
    sx, sy = start
    ex, ey = end
    
    # Altura de crucero del dron
    altura_vuelo = 180 
    
    waypoints = [(sx, sy, 0), (sx, sy, altura_vuelo)]
    
    # Heurística simple: ir directo, si hay colisión, rodear.
    # Para mantenerlo rápido y demostrativo, haremos un trazado simple en zig-zag.
    dx = ex - sx
    dy = ey - sy
    dist = math.hypot(dx, dy)
    
    if dist < 10:
        return [(sx, sy, 0), (ex, ey, 0)]
        
    pasos = int(dist / step)
    
    cx, cy = sx, sy
    for i in range(1, pasos):
        # Punto intermedio ideal
        t = i / pasos
        ix = sx + dx * t
        iy = sy + dy * t
        
        # Si el punto ideal colisiona con un edificio infinitamente alto, lo movemos
        if _hay_colision(ix, iy, edificios):
            # Intentar desviar a la derecha
            offset_x = -dy * 0.5
            offset_y = dx * 0.5
            if not _hay_colision(ix + offset_x, iy + offset_y, edificios):
                ix += offset_x
                iy += offset_y
            else:
                # Desviar a la izquierda
                ix -= offset_x
                iy -= offset_y
                
        # Solo agregar si es un quiebre significativo para no saturar Spline
        # Agregamos aleatoriedad controlada para simular el pathfinding real
        if i % 3 == 0:
            waypoints.append((ix, iy, altura_vuelo + random.uniform(-10, 10)))
            
    waypoints.append((ex, ey, altura_vuelo))
    waypoints.append((ex, ey, 0))
    
    return waypoints

def calcular_trayectoria_spline(waypoints):
    """
    Usa la clase CubicSplinesInterpolator para suavizar la ruta en 3D.
    Parametrizamos t = 0, 1, ..., N
    X(t) = Spline(t), Y(t) = Spline(t), Z(t) = Spline(t)
    """
    n_puntos = len(waypoints)
    if n_puntos < 3:
        return waypoints
        
    t_vals = np.arange(n_puntos)
    x_vals = [p[0] for p in waypoints]
    y_vals = [p[1] for p in waypoints]
    z_vals = [p[2] for p in waypoints]
    
    spline_x = CubicSplinesInterpolator(t_vals, x_vals)
    spline_x.calcular_splines()
    
    spline_y = CubicSplinesInterpolator(t_vals, y_vals)
    spline_y.calcular_splines()
    
    spline_z = CubicSplinesInterpolator(t_vals, z_vals)
    spline_z.calcular_splines()
    
    # Generar ruta densa (suave)
    t_densos = np.linspace(0, n_puntos - 1, 100)
    
    ruta_suave = []
    for t in t_densos:
        rx = spline_x._evaluar_spline(t)
        ry = spline_y._evaluar_spline(t)
        rz = spline_z._evaluar_spline(t)
        ruta_suave.append((rx, ry, rz))
        
    return ruta_suave

def integrar_simpson_discreto(y_data, h):
    """
    Implementación de la Regla de Simpson 1/3 para un arreglo de datos discretos.
    Retorna la integral acumulada para poder trazar la curva de posición.
    """
    n = len(y_data)
    integral_acumulada = [0.0]
    
    # Simpson compuesto para calcular el acumulado paso a paso.
    # Como Simpson requiere 3 puntos (2 subintervalos), avanzamos de a 2.
    suma_total = 0.0
    for i in range(2, n, 2):
        area_parcial = (h / 3) * (y_data[i-2] + 4*y_data[i-1] + y_data[i])
        suma_total += area_parcial
        integral_acumulada.append(suma_total)
        # Para mantener el mismo tamaño de array, interpolamos linealmente el punto intermedio
        # en la salida acumulada
        
    # Reconstruir array del mismo tamaño
    resultado = np.zeros(n)
    for i in range(2, n, 2):
        resultado[i] = integral_acumulada[i//2]
        resultado[i-1] = (resultado[i-2] + resultado[i]) / 2.0
        
    if n % 2 == 0:
        # Extrapolar el último si es par
        resultado[-1] = resultado[-2] + (resultado[-2] - resultado[-3])
        
    return resultado.tolist()

def generar_telemetria(ruta_suave, tiempo_total=None):
    """
    Genera datos de aceleración sintéticos basados en la ruta, 
    y demuestra que la doble integración por Simpson recupera la distancia.
    Velocidad de crucero realista: ~15 m/s (54 km/h) para dron comercial.
    """
    n_muestras = len(ruta_suave)
    
    # Calcular distancia total primero para determinar tiempo realista
    dist_total_pre = 0
    for i in range(1, n_muestras):
        ddx = ruta_suave[i][0] - ruta_suave[i-1][0]
        ddy = ruta_suave[i][1] - ruta_suave[i-1][1]
        ddz = ruta_suave[i][2] - ruta_suave[i-1][2]
        dist_total_pre += math.sqrt(ddx*ddx + ddy*ddy + ddz*ddz)
    
    # Velocidad de crucero realista (15 m/s ≈ 54 km/h, un dron DJI típico)
    velocidad_crucero = 15.0  # m/s
    if tiempo_total is None:
        tiempo_total = max(30, dist_total_pre / velocidad_crucero)
    
    h = tiempo_total / n_muestras
    
    # Calcular distancia total recorrida en la ruta (longitud de arco)
    dist_total = 0
    for i in range(1, n_muestras):
        dx = ruta_suave[i][0] - ruta_suave[i-1][0]
        dy = ruta_suave[i][1] - ruta_suave[i-1][1]
        dz = ruta_suave[i][2] - ruta_suave[i-1][2]
        dist_total += math.sqrt(dx*dx + dy*dy + dz*dz)
        
    # Crear un perfil de aceleración (trapezoide de velocidad)
    # 1. Acelera positivamente
    # 2. Aceleración cero (velocidad constante)
    # 3. Acelera negativamente (frena)
    aceleracion = np.zeros(n_muestras)
    tercio = n_muestras // 3
    
    # Ajustamos la magnitud de la aceleración para que la doble integral coincida con dist_total
    # v_max = a * t_accel. Dist = 0.5 * a * t_accel^2 + v_max * t_const + 0.5 * a * t_accel^2
    # Esto es demostrativo, así que inyectaremos ruido al final para el "drift" inercial.
    
    a_mag = dist_total / (tiempo_total * tiempo_total * 0.2)
    
    for i in range(tercio):
        aceleracion[i] = a_mag + random.uniform(-0.1, 0.1)
    for i in range(tercio, 2*tercio):
        aceleracion[i] = 0 + random.uniform(-0.1, 0.1)
    for i in range(2*tercio, n_muestras):
        aceleracion[i] = -a_mag + random.uniform(-0.1, 0.1)
        
    # 1. Primera integración de Simpson: Aceleración -> Velocidad
    velocidad = integrar_simpson_discreto(aceleracion, h)
    
    # 2. Segunda integración de Simpson: Velocidad -> Posición (Distancia Recorrida)
    posicion = integrar_simpson_discreto(velocidad, h)
    
    return {
        "aceleracion": list(aceleracion),
        "velocidad": velocidad,
        "posicion_integrada": posicion,
        "distancia_real": dist_total,
        "tiempo_total": tiempo_total,
        "dt": h
    }
