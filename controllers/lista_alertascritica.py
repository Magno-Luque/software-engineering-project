from flask import Blueprint, render_template, redirect, url_for, session, flash
from models.alertacritica import Alerta # Tu modelo Alerta
from datetime import timedelta, datetime # Importa timedelta y datetime

alertas_bp = Blueprint('alertas', __name__)

@alertas_bp.route('/paciente/alertas_criticas')
def listar_alertascritica():
    # 1. Obtener las alertas desde el Modelo
    alertas_raw = Alerta.obtener_alerta_por_usuario(session['user_id'])
    
    if alertas_raw is None:
        flash('No se encontraron alertas', 'info')
        return render_template('paciente/alertas_criticas.html', alertas=[])
    
    # 2. **Procesar las alertas y ajustar la hora en el Controller**
    alertas_procesadas = []
    if alertas_raw: # Asegúrate de que la lista no esté vacía
        for alerta_dict in alertas_raw:
            # `alerta_dict` es un diccionario, e.g., {'id': 1, 'fecha': datetime_obj, ...}
            
            # Verificar si la clave 'fecha' existe y es un objeto datetime
            if 'fecha' in alerta_dict and isinstance(alerta_dict['fecha'], datetime):
                # Resta 5 horas directamente a la fecha en el diccionario
                alerta_dict['fecha'] = alerta_dict['fecha'] - timedelta(hours=5)
            
            # Agrega el diccionario (ya modificado) a la nueva lista
            alertas_procesadas.append(alerta_dict)
            
    # 3. Renderizar la plantilla con las alertas procesadas
    return render_template('paciente/alertas_criticas.html', alertas=alertas_procesadas)