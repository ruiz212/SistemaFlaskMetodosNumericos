from flask import Blueprint

aplicacion_bp = Blueprint('aplicacion', __name__, template_folder='../templates', static_folder='../static')

from . import rutas
