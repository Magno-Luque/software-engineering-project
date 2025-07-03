# controllers/cita_paciente.py

from models.cita_paciente import CitaPaciente
from datetime import datetime, date, timedelta

def obtener_enfermedades_paciente(paciente_id):
    """Obtiene las enfermedades del paciente"""
    
    try:
        from app import mysql
        
        cursor = mysql.connection.cursor()
        
        # Consulta directa para obtener únicamente el ID
        cursor.execute("SELECT id FROM pacientes WHERE usuarios_id1 = %s LIMIT 1", (paciente_id,))
        
        id_paciente = cursor.fetchone()  # Obtiene la primera coincidencia
        cursor.close()
        
        enfermedades = CitaPaciente.obtener_enfermedades_asignadas(mysql, id_paciente['id'])
        
        return {
            'exito': True,
            'enfermedades': [{
                'id': e['id'],
                'codigo': e['codigo'],
                'nombre': e['nombre'],
                'descripcion': e.get('descripcion', ''),
                'especialidad_requerida': e['especialidad_requerida']
            } for e in enfermedades]
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'exito': False,
            'error': str(e),
            'enfermedades': []
        }

def obtener_horarios_disponibles_paciente(paciente_id, fecha_desde, fecha_hasta, especialidad=None):
    """Obtiene horarios disponibles para el paciente"""
    try:
        from app import mysql
        
        cursor = mysql.connection.cursor()
        
        # Consulta directa para obtener únicamente el ID
        cursor.execute("SELECT id FROM pacientes WHERE usuarios_id1 = %s LIMIT 1", (paciente_id,))
        
        id_paciente = cursor.fetchone()  # Obtiene la primera coincidencia
        cursor.close()
        
        # Validar fechas
        if not fecha_desde:
            fecha_desde = date.today()
        elif isinstance(fecha_desde, str):
            fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        
        if not fecha_hasta:
            fecha_hasta = fecha_desde + timedelta(days=30)
        elif isinstance(fecha_hasta, str):
            fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        
        horarios = CitaPaciente.obtener_horarios_disponibles(
            mysql, id_paciente['id'], fecha_desde, fecha_hasta, especialidad
        )
        
        # Organizar por fecha
        horarios_por_fecha = {}
        for horario in horarios:
            fecha_str = horario['fecha'].isoformat() if hasattr(horario['fecha'], 'isoformat') else str(horario['fecha'])
            
            if fecha_str not in horarios_por_fecha:
                horarios_por_fecha[fecha_str] = []
            
            horarios_por_fecha[fecha_str].append({
                'id': horario['id'],
                'hora_inicio': horario['hora_inicio'].strftime('%H:%M') if hasattr(horario['hora_inicio'], 'strftime') else str(horario['hora_inicio']),
                'hora_fin': horario['hora_fin'].strftime('%H:%M') if hasattr(horario['hora_fin'], 'strftime') else str(horario['hora_fin']),
                'tipo': horario['tipo'],
                'consultorio': horario.get('consultorio'),
                'medico': {
                    'id': horario['medico_id'],
                    'nombre': f"Dr. {horario['nombres']} {horario['apellidos']}",
                    'especialidad': horario['especialidad']
                },
                'enfermedad': {
                    'id': horario['enfermedad_id'],
                    'codigo': horario['enfermedad_codigo'],
                    'nombre': horario['enfermedad_nombre']
                }
            })
        
        return {
            'exito': True,
            'horarios_por_fecha': horarios_por_fecha,
            'total_horarios': len(horarios)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'exito': False,
            'error': str(e),
            'horarios_por_fecha': {},
            'total_horarios': 0
        }

def crear_cita_paciente(datos_cita):
    """Crea una nueva cita"""
    try:
        from app import mysql
        
        cursor = mysql.connection.cursor()
        
        # Consulta directa para obtener únicamente el ID
        cursor.execute("SELECT id FROM pacientes WHERE usuarios_id1 = %s LIMIT 1", (datos_cita['paciente_id'],))
        
        id_paciente = cursor.fetchone()  # Obtiene la primera coincidencia

        cursor.close()
        
        datos_cita['paciente_id'] = id_paciente['id']
        
        # Validar campos requeridos
        if not datos_cita.get('paciente_id'):
            return {'exito': False, 'error': 'ID de paciente requerido'}
        if not datos_cita.get('horario_id'):
            return {'exito': False, 'error': 'ID de horario requerido'}
        if not datos_cita.get('enfermedad_id'):
            return {'exito': False, 'error': 'ID de enfermedad requerido'}
        if not datos_cita.get('motivo_consulta'):
            return {'exito': False, 'error': 'Motivo de consulta requerido'}
        
        print(datos_cita)
        
        # Crear la cita
        resultado = CitaPaciente.crear_cita(mysql, datos_cita)
        
        return {
            'exito': True,
            'mensaje': 'Cita agendada exitosamente',
            'cita_id': resultado['cita_id'],
            'detalles': {
                'fecha': resultado['detalles']['fecha'].isoformat() if hasattr(resultado['detalles']['fecha'], 'isoformat') else str(resultado['detalles']['fecha']),
                'hora_inicio': resultado['detalles']['hora_inicio'].strftime('%H:%M') if hasattr(resultado['detalles']['hora_inicio'], 'strftime') else str(resultado['detalles']['hora_inicio']),
                'hora_fin': resultado['detalles']['hora_fin'].strftime('%H:%M') if hasattr(resultado['detalles']['hora_fin'], 'strftime') else str(resultado['detalles']['hora_fin']),
                'medico': resultado['detalles']['medico'],
                'especialidad': resultado['detalles']['especialidad'],
                'tipo': resultado['detalles']['tipo'],
                'consultorio': resultado['detalles']['consultorio'],
                'enlace_virtual': resultado['detalles']['enlace_virtual']
            }
        }
        
    except ValueError as ve:
        return {'exito': False, 'error': str(ve)}
    except Exception as e:
        print(f"Error: {str(e)}")
        return {'exito': False, 'error': f'Error interno: {str(e)}'}