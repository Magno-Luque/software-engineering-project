# controllers/paciente.py

from models.actores import Cita, Paciente
from datetime import datetime, date, timedelta

def obtener_dashboard_paciente(paciente_id):
    """
    Obtiene datos para el dashboard del paciente
    """
    try:
        from app import mysql
        
        # Obtener información del paciente
        paciente = Paciente.obtener_por_id(mysql, paciente_id)
        if not paciente:
            return crear_dashboard_vacio()
        
        # Obtener próximas citas (siguiente y las 3 más cercanas)
        proximas_citas = Cita.obtener_proximas_citas_paciente(mysql, paciente_id, limit=4)
        
        # Obtener citas de hoy
        citas_hoy = Cita.obtener_citas_hoy_paciente(mysql, paciente_id)
        
        # Obtener próxima cita (la más cercana)
        proxima_cita = proximas_citas[0] if proximas_citas else None
        
        # Estadísticas del paciente
        total_citas = Cita.contar_citas_paciente(mysql, paciente_id)
        citas_pendientes = Cita.contar_citas_pendientes_paciente(mysql, paciente_id)
        ultima_cita = Cita.obtener_ultima_cita_atendida(mysql, paciente_id)
        
        return {
            'paciente': {
                'id': paciente['id'],
                'nombre_completo': f"{paciente['nombres']} {paciente['apellidos']}",
                'dni': paciente['dni'],
                'email': paciente.get('email', ''),
                'telefono': paciente.get('telefono', ''),
                'edad': Paciente.calcular_edad(paciente['fecha_nacimiento']) if paciente.get('fecha_nacimiento') else None
            },
            'estadisticas': {
                'total_citas': total_citas,
                'citas_pendientes': citas_pendientes,
                'citas_hoy': len(citas_hoy)
            },
            'proxima_cita': formatear_cita_para_vista(proxima_cita) if proxima_cita else None,
            'citas_hoy': [formatear_cita_para_vista(cita) for cita in citas_hoy],
            'proximas_citas': [formatear_cita_para_vista(cita) for cita in proximas_citas],
            'ultima_cita': formatear_cita_para_vista(ultima_cita) if ultima_cita else None
        }
        
    except Exception as e:
        print(f"Error en obtener_dashboard_paciente: {str(e)}")
        return crear_dashboard_vacio()

def obtener_citas_paciente(paciente_id, estado='todas', limite=10):
    """
    Obtiene las citas del paciente filtradas por estado
    """
    try:
        from app import mysql
        
        citas = Cita.obtener_citas_por_paciente(mysql, paciente_id, estado, limite)
        
        return [formatear_cita_para_vista(cita) for cita in citas]
        
    except Exception as e:
        print(f"Error en obtener_citas_paciente: {str(e)}")
        return []

def obtener_proximas_citas_paciente(paciente_id, dias=30):
    """
    Obtiene las próximas citas del paciente en los próximos X días
    """
    try:
        from app import mysql
        
        citas = Cita.obtener_proximas_citas_paciente(mysql, paciente_id, dias)
        
        return [formatear_cita_para_vista(cita) for cita in citas]
        
    except Exception as e:
        print(f"Error en obtener_proximas_citas_paciente: {str(e)}")
        return []

def formatear_cita_para_vista(cita):
    """
    Formatea una cita para ser mostrada en la vista
    """
    if not cita:
        return None
    
    try:
        # Formatear fecha
        fecha_cita = cita['fecha_cita']
        if isinstance(fecha_cita, str):
            fecha_obj = datetime.strptime(fecha_cita, '%Y-%m-%d').date()
        else:
            fecha_obj = fecha_cita
        
        # Formatear hora
        hora_inicio = str(cita['hora_inicio'])
        hora_fin = str(cita['hora_fin'])
        
        # Calcular tiempo hasta la cita
        tiempo_hasta_cita = calcular_tiempo_hasta_cita(fecha_obj, hora_inicio)
        
        # Determinar color según el tipo y estado
        color_estado = obtener_color_estado_cita(cita['estado'], cita['tipo'])
        
        return {
            'id': cita['id'],
            'fecha_cita': fecha_obj.strftime('%d/%m/%Y'),
            'fecha_cita_iso': fecha_obj.isoformat(),
            'dia_semana': obtener_dia_semana(fecha_obj),
            'hora_inicio': hora_inicio,
            'hora_fin': hora_fin,
            'duracion_minutos': cita['duracion_minutos'],
            'tipo': cita['tipo'],
            'tipo_texto': 'Virtual' if cita['tipo'] == 'VIRTUAL' else 'Presencial',
            'estado': cita['estado'],
            'estado_texto': obtener_texto_estado(cita['estado']),
            'especialidad': cita['especialidad'],
            'consultorio': cita.get('consultorio', ''),
            'medico_nombre': f"Dr. {cita.get('medico_nombres', '')} {cita.get('medico_apellidos', '')}".strip(),
            'enfermedad': cita.get('enfermedad_nombre', ''),
            'motivo_consulta': cita.get('motivo_consulta', ''),
            'observaciones': cita.get('observaciones', ''),
            'enlace_virtual': cita.get('enlace_virtual', ''),
            'tiempo_hasta_cita': tiempo_hasta_cita,
            'color_estado': color_estado,
            'es_hoy': fecha_obj == date.today(),
            'es_manana': fecha_obj == date.today() + timedelta(days=1),
            'es_proxima_semana': fecha_obj <= date.today() + timedelta(days=7)
        }
        
    except Exception as e:
        print(f"Error al formatear cita: {str(e)}")
        return None

def crear_dashboard_vacio():
    """
    Crea un dashboard vacío en caso de error
    """
    return {
        'paciente': None,
        'estadisticas': {
            'total_citas': 0,
            'citas_pendientes': 0,
            'citas_hoy': 0
        },
        'proxima_cita': None,
        'citas_hoy': [],
        'proximas_citas': [],
        'ultima_cita': None
    }

# Funciones auxiliares

def calcular_tiempo_hasta_cita(fecha_cita, hora_cita):
    """
    Calcula el tiempo que falta hasta una cita
    """
    try:
        # Combinar fecha y hora
        hora_obj = datetime.strptime(hora_cita, '%H:%M:%S').time()
        datetime_cita = datetime.combine(fecha_cita, hora_obj)
        
        # Calcular diferencia
        ahora = datetime.now()
        diferencia = datetime_cita - ahora
        
        if diferencia.days < 0:
            return "Cita pasada"
        elif diferencia.days == 0:
            if diferencia.seconds < 3600:  # Menos de 1 hora
                minutos = diferencia.seconds // 60
                return f"En {minutos} minutos"
            else:
                horas = diferencia.seconds // 3600
                return f"En {horas} horas"
        elif diferencia.days == 1:
            return "Mañana"
        elif diferencia.days <= 7:
            return f"En {diferencia.days} días"
        else:
            return f"En {diferencia.days} días"
            
    except Exception as e:
        print(f"Error al calcular tiempo hasta cita: {str(e)}")
        return "Tiempo no disponible"

def obtener_dia_semana(fecha):
    """
    Obtiene el nombre del día de la semana
    """
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    return dias[fecha.weekday()]

def obtener_texto_estado(estado):
    """
    Convierte el estado de la cita a texto legible
    """
    estados = {
        'AGENDADA': 'Agendada',
        'ATENDIDA': 'Atendida',
        'NO_ATENDIDA': 'No atendida',
        'CANCELADA': 'Cancelada'
    }
    return estados.get(estado, estado)

def obtener_color_estado_cita(estado, tipo):
    """
    Obtiene el color para mostrar la cita según su estado y tipo
    """
    if estado == 'AGENDADA':
        return 'blue' if tipo == 'VIRTUAL' else 'green'
    elif estado == 'ATENDIDA':
        return 'success'
    elif estado == 'CANCELADA':
        return 'danger'
    elif estado == 'NO_ATENDIDA':
        return 'warning'
    else:
        return 'secondary'