import requests
from datetime import datetime

def obtener_datos_clima(latitud, longitud):
    """
    Se conecta a la API de Open-Meteo para obtener los datos de radiación solar.
    No requiere API Key.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitud}&longitude={longitud}&hourly=direct_radiation,diffuse_radiation,temperature_2m&timezone=auto&forecast_days=1"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extraemos las horas y la radiación
        tiempos = data["hourly"]["time"]
        radiacion_directa = data["hourly"]["direct_radiation"]
        temperatura = data["hourly"]["temperature_2m"]
        
        # Formatear datos para el frontend y los métodos
        datos_hora = []
        for i in range(len(tiempos)):
            # Convertir string ISO a hora legible
            hora_dt = datetime.fromisoformat(tiempos[i])
            hora_str = hora_dt.strftime("%H:%M")
            
            datos_hora.append({
                "hora": hora_str,
                "radiacion": radiacion_directa[i],
                "temperatura": temperatura[i]
            })
            
        return {
            "success": True,
            "latitud": latitud,
            "longitud": longitud,
            "datos_horarios": datos_hora,
            "max_radiacion": max(radiacion_directa) if radiacion_directa else 0
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Error de conexión con la API del Clima: {str(e)}"
        }
