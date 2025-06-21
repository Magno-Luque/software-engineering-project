# controllers/admin_dashboard.py

from models.admin_dashboard import ResumenDashboard, Cita
from models.actores import Paciente, Profesional

# ------------------------------------------------------------------------------
# FUNCIÓN: obtener_resumen_dashboard
# Propósito: Obtiene métricas del dashboard desde el modelo o devuelve valores por defecto
# Comportamiento:
#   - Usa el modelo ResumenDashboard para obtener datos
#   - Retorna ceros si no hay registro en la base de datos
# ------------------------------------------------------------------------------
def obtener_resumen_dashboard():
    """
    Retorna el resumen de métricas para el panel de administración.
    
    Returns:
        dict: Diccionario con métricas del dashboard o valores por defecto
        
    Notas:
        - Valores por defecto se usan cuando no existe registro en la base
        - La lógica de cálculo está en el modelo, no aquí
    """
    resumen = ResumenDashboard.obtener_resumen()
    return resumen if resumen else {
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
        - Los campos devueltos: dni, nombres, apellidos, estado
        - Ordenado por fecha de registro descendente
    """
    pacientes = Paciente.obtener_pacientes_recientes(limit)
    return [{
        'dni': paciente.dni,
        'nombres': paciente.nombres,
        'apellidos': paciente.apellidos,
        'estado': paciente.estado
    } for paciente in pacientes]

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
        - Datos del médico (nombres, apellidos, nombre_formal, especialidad)
        
    Notas:
        - Ordenado por hora de la cita ascendente
        - Usa relaciones para acceder a datos de paciente y médico
    """
    citas = Cita.obtener_citas_hoy()
    return [{
        'paciente_dni': cita.paciente.dni,
        'paciente_nombres': cita.paciente.nombres,
        'paciente_apellidos': cita.paciente.apellidos,
        'fecha_cita': cita.fecha_cita,
        'horario_id': cita.horario_id,
        'hora_inicio': cita.hora_inicio, 
        'hora_fin': cita.hora_fin,        
        'horario_completo': cita.horario_completo,  # NUEVO: propiedad que formatea el horario
        'duracion_formateada': cita.duracion_formateada,  # NUEVO: duración legible
        'estado': cita.estado,
        'nombres_medico': cita.medico.nombres,
        'apellidos_medico': cita.medico.apellidos,
        'nombre_formal': cita.medico.nombre_formal,
        'especialidad': cita.especialidad,  
        'tipo': cita.tipo,                 
        'consultorio': cita.consultorio,   
        'motivo_consulta': cita.motivo_consulta  
    } for cita in citas]