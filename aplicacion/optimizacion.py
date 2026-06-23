import math
from metodos.newton_raphson import newton_raphson
from metodos.integracion import integrar

def calcular_angulo_optimo(latitud, max_radiacion):
    """
    Simula una función de energía E(theta) para un panel solar inclinado a theta grados.
    Queremos maximizar E(theta), así que buscamos la raíz de su derivada E'(theta) = 0.
    
    E(theta) = max_radiacion * cos(theta - latitud) + 50 * sin(2*theta)
    E'(theta) = -max_radiacion * sin(theta - latitud) + 100 * cos(2*theta)
    E''(theta) = -max_radiacion * cos(theta - latitud) - 200 * sin(2*theta)
    """
    
    # Trabajamos en radianes internamente
    lat_rad = math.radians(latitud)
    
    def f_prima(theta):
        return -max_radiacion * math.sin(theta - lat_rad) + 100 * math.cos(2*theta)
        
    def f_biprima(theta):
        return -max_radiacion * math.cos(theta - lat_rad) - 200 * math.sin(2*theta)
        
    # Valor inicial: sugerimos la misma latitud como inclinación inicial (regla de oro solar)
    ci = lat_rad
    tol = 0.001
    
    if max_radiacion <= 0:
        return {
            "angulo": 0.0,
            "pasos": [{"iter": 1, "ci": ci, "fci": 0, "dfci": 0, "cimas1": 0, "error": 0}]
        }
        
    # Buscamos la raíz de f_prima usando Newton-Raphson
    res = newton_raphson(ci, tol, f_prima, f_biprima)
    
    if "error" in res:
        return {"error": res["error"]}
        
    # Extraemos el último valor de la tabla de resultados
    resultados = res["resultados"]
    if resultados:
        ultima_fila = resultados[-1]
        angulo_rad = float(ultima_fila['cimas1']) # xi
        angulo_deg = math.degrees(angulo_rad)
        
        # Limitamos entre 0 y 90 grados
        angulo_deg = max(0, min(90, angulo_deg))
        
        return {
            "angulo": round(angulo_deg, 2),
            "pasos": res["resultados"]
        }
    return {"error": "No se encontró un ángulo óptimo."}

def calcular_energia_total(datos_horarios, coeficiente_temp=0.0):
    """
    Aproxima la energía generada integrando los datos de radiación.
    Aplica una penalización térmica matemática si la temperatura > 25°C 
    basada en la constante de fábrica del panel.
    """
    y_vals_ideal = []
    y_vals_real = []
    
    for d in datos_horarios:
        rad = d["radiacion"]
        temp = d.get("temperatura", 25.0)
        y_vals_ideal.append(rad)
        
        # Modelo térmico simplificado
        if temp > 25.0:
            # el coeficiente suele venir en %, por lo que dividimos por 100
            perdida_porcentaje = abs(coeficiente_temp) / 100.0 * (temp - 25.0)
            rad_real = rad * (1.0 - perdida_porcentaje)
        else:
            rad_real = rad
            
        y_vals_real.append(rad_real)

    if len(y_vals_ideal) < 2:
        return {"energia_ideal": 0, "energia_real": 0, "energia_perdida": 0, "energia_real_romberg": 0, "curva_real": []}
        
    # Regla del trapecio (h = 1 hora)
    h = 1
    suma_interna_ideal = sum(y_vals_ideal[1:-1])
    integral_ideal = (h / 2) * (y_vals_ideal[0] + 2 * suma_interna_ideal + y_vals_ideal[-1])
    
    suma_interna_real = sum(y_vals_real[1:-1])
    integral_real = (h / 2) * (y_vals_real[0] + 2 * suma_interna_real + y_vals_real[-1])
    
    energia_perdida = integral_ideal - integral_real
    
    # --- MÉTODO DE ROMBERG ---
    import numpy as np
    from metodos.integracion import romberg
    
    x_vals = np.arange(len(y_vals_real))
    
    def f_real(t):
        return np.interp(t, x_vals, y_vals_real)
        
    # Usamos 5 niveles para Romberg, integrando desde 0 hasta el último índice (típicamente 23)
    res_romberg = romberg(0, len(x_vals)-1, 5, f_real)
    energia_real_romberg = res_romberg["integral"] if "error" not in res_romberg else integral_real

    return {
        "energia_ideal": round(integral_ideal, 2),
        "energia_real": round(integral_real, 2),
        "energia_perdida": round(energia_perdida, 2),
        "energia_real_romberg": round(energia_real_romberg, 2),
        "curva_real": [round(val, 2) for val in y_vals_real]
    }
