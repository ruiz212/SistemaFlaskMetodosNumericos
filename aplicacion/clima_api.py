import requests
from datetime import datetime

def obtener_datos_clima(latitud, longitud):
    """
    Se conecta a la API de Open-Meteo para obtener los datos de radiación solar.
    No requiere API Key.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitud}&longitude={longitud}&hourly=direct_radiation,diffuse_radiation,temperature_2m&timezone=auto&forecast_days=1"
    
    try:
        headers = {
            "User-Agent": "ProyectoFlaskMetodos/1.0 (SolarPanelIoT)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extraemos las horas y la radiación
        tiempos = data.get("hourly", {}).get("time", [])
        radiacion_directa = data.get("hourly", {}).get("direct_radiation", [])
        temperatura = data.get("hourly", {}).get("temperature_2m", [])
        
        # Formatear datos para el frontend y los métodos
        datos_hora = []
        for i in range(len(tiempos)):
            # Extraemos la hora directamente del string ISO "YYYY-MM-DDTHH:MM" (para evitar errores con fromisoformat en versiones viejas de Python)
            hora_str = tiempos[i][11:16] if len(tiempos[i]) >= 16 else "00:00"
            
            rad_val = radiacion_directa[i] if i < len(radiacion_directa) and radiacion_directa[i] is not None else 0
            temp_val = temperatura[i] if i < len(temperatura) and temperatura[i] is not None else 25.0
            
            datos_hora.append({
                "hora": hora_str,
                "radiacion": rad_val,
                "temperatura": temp_val
            })
            
        return {
            "success": True,
            "latitud": latitud,
            "longitud": longitud,
            "datos_horarios": datos_hora,
            "max_radiacion": max([d["radiacion"] for d in datos_hora]) if datos_hora else 0
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Error de red con la API del Clima: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error procesando datos del Clima: {str(e)}"
        }
