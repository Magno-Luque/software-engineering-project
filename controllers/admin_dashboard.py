# controllers/admin_dashboard.py

from models.admin_dashboard import ResumenDashboard
from models.actores import Paciente
from models.cita import Cita

# ------------------------------------------------------------------------------
# FUNCIÓN: obtener_resumen_dashboard
# Propósito: Obtiene métricas del dashboard desde el modelo o devuelve valores por defecto
# Comportamiento:
#   - Usa el modelo ResumenDashboard para obtener datos en tiempo real
#   - Retorna ceros si hay error en la consulta
# ------------------------------------------------------------------------------
def obtener_resumen_dashboard():
    """
    Retorna el resumen de métricas para el panel de administración.
    
    Returns:
        dict: Diccionario con métricas del dashboard o valores por defecto
        
    Notas:
        - Calcula métricas en tiempo real para mayor precisión
        - La lógica de cálculo está en el modelo, no aquí
    """
    try:
        from app import mysql
        resumen = ResumenDashboard.obtener_resumen(mysql)
        return resumen if resumen else {
            'total_pacientes': 0,
            'total_profesionales': 0,
            'total_citas_hoy': 0,
            'total_alertas_criticas': 0
        }
    except Exception as e:
        print(f"Error en obtener_resumen_dashboard: {str(e)}")
        return {
            'total_pacientes': 0,
            'total_profesionales': 0,
            'total_citas_hoy': 0,
            'total_alertas_criticas': 0
        }

# ------------------------------------------------------------------------------
# FUNCIÓN: obtener_pacientes_recientes
# Propósito: Obtiene los últimos pacientes registrados en formato serializado
# ------------------------------------------------------------------------------
def obtener_pacientes_recientes(limit=5):
    """
    Obtiene los pacientes más recientes registrados en el sistema.
    
    Args:
        limit (int): Número máximo de pacientes a retornar (default: 5)
        
    Returns:
        list[dict]: Lista de diccionarios con datos básicos de pacientes
        
    Notas:
        - Los campos devueltos: dni, nombres, apellidos, estado, fecha_registro
        - Ordenado por fecha de registro descendente
    """
    try:
        from app import mysql
        pacientes = Paciente.obtener_pacientes_recientes(mysql, limit)
        return [{
            'dni': paciente['dni'],
            'nombres': paciente['nombres'],
            'apellidos': paciente['apellidos'],
            'estado': paciente['estado']
        } for paciente in pacientes]
    except Exception as e:
        print(f"Error en obtener_pacientes_recientes: {str(e)}")
        return []

# ------------------------------------------------------------------------------
# FUNCIÓN: obtener_citas_hoy
# Propósito: Obtiene citas del día actual con datos relacionados serializados
# ------------------------------------------------------------------------------
def obtener_citas_hoy():
    """
    Obtiene las citas programadas para hoy con datos de paciente y médico.
    
    Returns:
        list[dict]: Lista de diccionarios con datos completos de citas
        
    Campos incluidos:
        - Datos del paciente (dni, nombres, apellidos)
        - Detalles de la cita (fecha, hora_inicio, hora_fin, estado)
        - Datos del médico (nombres, apellidos, especialidad)
        
    Notas:
        - Ordenado por hora de la cita ascendente
        - Usa JOINs para obtener datos relacionados
        - Incluye formateo de horarios y duración
    """
    try:
        from app import mysql
        citas = Cita.obtener_citas_hoy(mysql)
        return [{
            'paciente_dni': cita.get('paciente_dni', ''),
            'paciente_nombres': cita.get('paciente_nombres', ''),
            'paciente_apellidos': cita.get('paciente_apellidos', ''),
            'fecha_cita': cita['fecha_cita'],
            'horario_id': cita['horario_id'],
            'hora_inicio': cita['hora_inicio'], 
            'hora_fin': cita['hora_fin'],        
            'horario_completo': Cita.formatear_horario_completo(cita['hora_inicio'], cita['hora_fin']),
            'duracion_formateada': Cita.formatear_duracion(cita['duracion_minutos']),
            'estado': cita['estado'],
            'nombres_medico': cita.get('medico_nombres', ''),
            'apellidos_medico': cita.get('medico_apellidos', ''),
            'nombre_formal': f"Dr. {cita.get('medico_nombres', '')} {cita.get('medico_apellidos', '')}".strip(),
            'especialidad': cita['especialidad'],  
            'tipo': cita['tipo'],                 
            'consultorio': cita['consultorio'],   
            'motivo_consulta': cita['motivo_consulta']  
        } for cita in citas]
    except Exception as e:
        print(f"Error en obtener_citas_hoy: {str(e)}")
        return []