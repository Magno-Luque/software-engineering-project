# controllers/medico.py

from models.actores import Cita, Paciente, PacienteEnfermedadMedico, AlertaCritica
from datetime import datetime, date, timedelta

def obtener_dashboard_medico(medico_id):
    """
    Obtiene datos para el dashboard del médico
    """
    try:
        from app import mysql
        
        # Estadísticas básicas
        total_pacientes = Paciente.contar_pacientes_asignados(mysql, medico_id)
        citas_hoy = Cita.contar_citas_hoy(mysql, medico_id)
        alertas_criticas = AlertaCritica.contar_alertas_pendientes(mysql, medico_id)
        
        # Citas próximas de hoy
        citas_hoy_detalle = Cita.obtener_citas_hoy(mysql, medico_id)
        
        # Alertas críticas pendientes
        alertas_pendientes = AlertaCritica.obtener_alertas_pendientes(mysql, medico_id)
        
        # Pacientes con mayor riesgo
        pacientes_riesgo = Paciente.obtener_pacientes_alto_riesgo(mysql, medico_id)
        
        return {
            'estadisticas': {
                'total_pacientes': total_pacientes,
                'citas_hoy': citas_hoy,
                'alertas_criticas': alertas_criticas,
                'adherencia_promedio': calcular_adherencia_promedio(mysql, medico_id)
            },
            'citas_hoy': citas_hoy_detalle,
            'alertas_pendientes': alertas_pendientes,
            'pacientes_riesgo': pacientes_riesgo
        }
        
    except Exception as e:
        print(f"Error en obtener_dashboard_medico: {str(e)}")
        return {
            'estadisticas': {
                'total_pacientes': 0,
                'citas_hoy': 0,
                'alertas_criticas': 0,
                'adherencia_promedio': 0
            },
            'citas_hoy': [],
            'alertas_pendientes': [],
            'pacientes_riesgo': []
        }

def obtener_pacientes_asignados(medico_id):
    """
    Obtiene todos los pacientes asignados al médico
    """
    try:
        from app import mysql
        
        # Obtener pacientes a través de la tabla de asignaciones
        pacientes = PacienteEnfermedadMedico.obtener_pacientes_por_medico(mysql, medico_id)
        
        # Enriquecer datos de cada paciente
        pacientes_enriquecidos = []
        for paciente in pacientes:
            # Obtener datos adicionales del paciente
            paciente_completo = Paciente.obtener_por_id(mysql, paciente['id'])
            
            if paciente_completo:
                # Calcular edad
                edad = Paciente.calcular_edad(paciente_completo['fecha_nacimiento'])
                
                # Obtener última actividad (última cita o registro biométrico)
                ultima_actividad = obtener_ultima_actividad_paciente(mysql, paciente['id'])
                
                # Calcular nivel de riesgo
                nivel_riesgo = calcular_nivel_riesgo_paciente(mysql, paciente['id'])
                
                # Calcular adherencia
                adherencia = calcular_adherencia_paciente(mysql, paciente['id'])
                
                pacientes_enriquecidos.append({
                    'id': paciente['id'],
                    'dni': paciente_completo['dni'],
                    'nombre_completo': f"{paciente_completo['nombres']} {paciente_completo['apellidos']}",
                    'edad': edad,
                    'enfermedad_principal': paciente['enfermedad_nombre'],
                    'nivel_riesgo': nivel_riesgo,
                    'ultima_actividad': ultima_actividad,
                    'adherencia': adherencia,
                    'estado': paciente_completo['estado']
                })
        
        return pacientes_enriquecidos
        
    except Exception as e:
        print(f"Error en obtener_pacientes_asignados: {str(e)}")
        return []

def obtener_citas_medico(medico_id, fecha=None, estado='todas'):
    """
    Obtiene las citas del médico filtradas por fecha y estado
    """
    try:
        from app import mysql
        
        if fecha:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        else:
            fecha_obj = date.today()
        
        # Obtener citas del médico
        citas = Cita.obtener_citas_por_medico_fecha(mysql, medico_id, fecha_obj, estado)
        
        # Formatear citas para la vista
        citas_formateadas = []
        for cita in citas:
            citas_formateadas.append({
                'id': cita['id'],
                'paciente_id': cita['paciente_id'],
                'paciente_nombre': f"{cita['paciente_nombres']} {cita['paciente_apellidos']}",
                'fecha_cita': cita['fecha_cita'].isoformat() if hasattr(cita['fecha_cita'], 'isoformat') else str(cita['fecha_cita']),
                'hora_inicio': str(cita['hora_inicio']),
                'hora_fin': str(cita['hora_fin']),
                'duracion_minutos': cita['duracion_minutos'],
                'tipo': cita['tipo'],
                'estado': cita['estado'],
                'especialidad': cita['especialidad'],
                'motivo_consulta': cita.get('motivo_consulta', ''),
                'observaciones': cita.get('observaciones', ''),
                'enlace_virtual': cita.get('enlace_virtual', ''),
                'consultorio': cita.get('consultorio', ''),
                'enfermedad': cita.get('enfermedad_nombre', '')
            })
        
        return citas_formateadas
        
    except Exception as e:
        print(f"Error en obtener_citas_medico: {str(e)}")
        return []

def obtener_citas_hoy(medico_id):
    """
    Obtiene las citas de hoy del médico
    """
    try:
        hoy = date.today()
        return obtener_citas_medico(medico_id, hoy.isoformat(), 'AGENDADA')
        
    except Exception as e:
        print(f"Error en obtener_citas_hoy: {str(e)}")
        return []

def obtener_alertas_criticas_medico(medico_id):
    """
    Obtiene las alertas críticas pendientes para los pacientes del médico
    """
    try:
        from app import mysql
        
        alertas = AlertaCritica.obtener_alertas_pendientes(mysql, medico_id)
        
        # Formatear alertas para la vista
        alertas_formateadas = []
        for alerta in alertas:
            alertas_formateadas.append({
                'id': alerta['id'],
                'paciente_id': alerta['paciente_id'],
                'paciente_nombre': f"{alerta['paciente_nombres']} {alerta['paciente_apellidos']}",
                'tipo_alerta': alerta['tipo_alerta'],
                'valor_registrado': alerta['valor_registrado'],
                'criticidad': alerta['criticidad'],
                'fecha_alerta': alerta['fecha_alerta'].strftime('%d/%m/%Y %H:%M') if hasattr(alerta['fecha_alerta'], 'strftime') else str(alerta['fecha_alerta']),
                'tiempo_transcurrido': calcular_tiempo_transcurrido(alerta['fecha_alerta']),
                'observaciones': alerta.get('observaciones', '')
            })
        
        return alertas_formateadas
        
    except Exception as e:
        print(f"Error en obtener_alertas_criticas_medico: {str(e)}")
        return []

# Funciones auxiliares

def calcular_adherencia_promedio(mysql, medico_id):
    """
    Calcula la adherencia promedio de todos los pacientes del médico
    """
    try:
        # Obtener pacientes del médico
        pacientes = PacienteEnfermedadMedico.obtener_pacientes_por_medico(mysql, medico_id)
        
        if not pacientes:
            return 0
        
        total_adherencia = 0
        count = 0
        
        for paciente in pacientes:
            adherencia = calcular_adherencia_paciente(mysql, paciente['id'])
            if adherencia > 0:
                total_adherencia += adherencia
                count += 1
        
        return round(total_adherencia / count if count > 0 else 0, 1)
        
    except Exception as e:
        print(f"Error al calcular adherencia promedio: {str(e)}")
        return 0

def calcular_adherencia_paciente(mysql, paciente_id):
    """
    Calcula la adherencia de un paciente específico
    """
    try:
        cursor = mysql.connection.cursor()
        
        # Simular cálculo de adherencia basado en registros biométricos
        # En una implementación real, esto sería más complejo
        query = """
            SELECT COUNT(*) as registros_mes
            FROM registros_biometricos
            WHERE paciente_id = %s 
            AND fecha_registro >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        """
        cursor.execute(query, (paciente_id,))
        resultado = cursor.fetchone()
        cursor.close()
        
        registros_mes = resultado['registros_mes'] if resultado else 0
        
        # Calcular adherencia (asumiendo que debería tener al menos 1 registro por día)
        adherencia = min(100, (registros_mes / 30) * 100)
        
        return round(adherencia, 1)
        
    except Exception as e:
        print(f"Error al calcular adherencia del paciente: {str(e)}")
        return 0

def calcular_nivel_riesgo_paciente(mysql, paciente_id):
    """
    Calcula el nivel de riesgo de un paciente
    """
    try:
        cursor = mysql.connection.cursor()
        
        # Verificar alertas críticas recientes
        query = """
            SELECT COUNT(*) as alertas_criticas
            FROM alertas_criticas
            WHERE paciente_id = %s 
            AND criticidad = 'ALTA'
            AND fecha_alerta >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            AND estado = 'PENDIENTE'
        """
        cursor.execute(query, (paciente_id,))
        resultado = cursor.fetchone()
        cursor.close()
        
        alertas_criticas = resultado['alertas_criticas'] if resultado else 0
        
        # Determinar nivel de riesgo
        if alertas_criticas >= 3:
            return 'ALTO'
        elif alertas_criticas >= 1:
            return 'MEDIO'
        else:
            return 'BAJO'
            
    except Exception as e:
        print(f"Error al calcular nivel de riesgo: {str(e)}")
        return 'BAJO'

def obtener_ultima_actividad_paciente(mysql, paciente_id):
    """
    Obtiene la fecha de la última actividad del paciente
    """
    try:
        cursor = mysql.connection.cursor()
        
        # Buscar la última cita atendida o el último registro biométrico
        query = """
            (SELECT fecha_actualizacion as ultima_fecha, 'cita' as tipo
             FROM citas 
             WHERE paciente_id = %s AND estado = 'ATENDIDA'
             ORDER BY fecha_actualizacion DESC 
             LIMIT 1)
            UNION
            (SELECT fecha_registro as ultima_fecha, 'biometrico' as tipo
             FROM registros_biometricos 
             WHERE paciente_id = %s
             ORDER BY fecha_registro DESC 
             LIMIT 1)
            ORDER BY ultima_fecha DESC 
            LIMIT 1
        """
        cursor.execute(query, (paciente_id, paciente_id))
        resultado = cursor.fetchone()
        cursor.close()
        
        if resultado:
            fecha = resultado['ultima_fecha']
            if hasattr(fecha, 'strftime'):
                return fecha.strftime('%d/%m/%Y %H:%M')
            else:
                return str(fecha)
        else:
            return 'Sin actividad reciente'
            
    except Exception as e:
        print(f"Error al obtener última actividad: {str(e)}")
        return 'Error al obtener datos'

def calcular_tiempo_transcurrido(fecha_alerta):
    """
    Calcula el tiempo transcurrido desde una alerta
    """
    try:
        if isinstance(fecha_alerta, str):
            fecha_alerta = datetime.strptime(fecha_alerta, '%Y-%m-%d %H:%M:%S')
        
        ahora = datetime.now()
        diferencia = ahora - fecha_alerta
        
        if diferencia.days > 0:
            return f"Hace {diferencia.days} días"
        elif diferencia.seconds > 3600:
            horas = diferencia.seconds // 3600
            return f"Hace {horas} horas"
        else:
            minutos = diferencia.seconds // 60
            return f"Hace {minutos} min"
            
    except Exception as e:
        print(f"Error al calcular tiempo transcurrido: {str(e)}")
        return "Tiempo no disponible"