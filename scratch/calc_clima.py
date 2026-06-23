import sys
import os

# Asegurarse de que el directorio principal esté en el sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aplicacion.clima_api import obtener_datos_clima
from aplicacion.optimizacion import calcular_angulo_optimo, calcular_energia_total

lat = 12.1462
lon = -86.2782
coef = -0.45

clima = obtener_datos_clima(lat, lon)
if not clima.get('success'):
    print("Error obteniendo clima:", clima)
    sys.exit(1)

energia = calcular_energia_total(clima["datos_horarios"], coef)
max_rad = clima["max_radiacion"]
optimizacion = calcular_angulo_optimo(lat, max_rad)

import json
print(json.dumps({
    "max_radiacion": max_rad,
    "energia_ideal": energia.get("energia_ideal"),
    "energia_real": energia.get("energia_real"),
    "energia_real_romberg": energia.get("energia_real_romberg"),
    "energia_perdida": energia.get("energia_perdida"),
    "angulo_optimo": optimizacion.get("angulo"),
    "error_optimizacion": optimizacion.get("error")
}, indent=4))
