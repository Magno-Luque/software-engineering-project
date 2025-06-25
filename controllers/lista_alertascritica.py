from flask import Blueprint, render_template, redirect, url_for, session, flash
from models.alertacritica import Alerta
from datetime import timedelta, datetime

alertas_bp = Blueprint('alertas', __name__)

@alertas_bp.route('/paciente/alertas_criticas')
def listar_alertascritica():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'error')
        return redirect(url_for('auth.login'))

    try:
        # 1. Obtener las alertas desde el Modelo
        alertas_raw = Alerta.obtener_alerta_por_usuario(session['user_id'])
        
        if not alertas_raw:  # Si está vacío o es None
            flash('No se encontraron alertas críticas', 'info')
            return render_template('paciente/alertas_criticas.html', alertas=[])
        
        # 2. Procesar las alertas y ajustar la hora
        alertas_procesadas = []
        for alerta_dict in alertas_raw:
            # Ajustar la zona horaria (5 horas menos)
            if 'fecha_alerta' in alerta_dict and isinstance(alerta_dict['fecha_alerta'], datetime):
                alerta_dict['fecha_alerta'] = alerta_dict['fecha_alerta'] - timedelta(hours=5)
            
            # Convertir ENUMs a strings más legibles si es necesario
            alerta_dict['tipo_alerta'] = alerta_dict['tipo_alerta'].replace('_', ' ').title()
            alerta_dict['criticidad'] = alerta_dict['criticidad'].capitalize()
            
            alertas_procesadas.append(alerta_dict)
            
        # 3. Ordenar por fecha más reciente (por si acaso)
        alertas_procesadas.sort(key=lambda x: x['fecha_alerta'], reverse=True)
        
        return render_template('paciente/alertas_criticas.html', 
                             alertas=alertas_procesadas,
                             ahora=datetime.now() - timedelta(hours=5))  # Hora actual ajustada

    except Exception as e:
        flash(f'Error al obtener alertas: {str(e)}', 'error')
        return render_template('paciente/alertas_criticas.html', alertas=[])