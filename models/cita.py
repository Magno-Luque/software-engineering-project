# models/cita.py

from datetime import datetime, date

class Cita:
    """Modelo para la tabla citas usando Flask-MySQLdb"""
    
    def __init__(self, mysql):
        self.mysql = mysql
     
    @classmethod
    def cancelar_cita(cls, mysql, cita_id):
        """Cancela una cita y libera el horario"""
        try:
            cursor = mysql.connection.cursor()
            
            # Obtener la cita
            query_cita = "SELECT * FROM citas WHERE id = %s"
            cursor.execute(query_cita, (cita_id,))
            cita = cursor.fetchone()
            
            if not cita:
                cursor.close()
                return {'success': False, 'error': 'Cita no encontrada'}
            
            if cita['estado'] == 'CANCELADA':
                cursor.close()
                return {'success': False, 'error': 'Cita ya cancelada'}
            
            # Liberar el horario
            query_liberar_horario = """
                UPDATE horarios_disponibles 
                SET estado = 'ACTIVO' 
                WHERE id = %s
            """
            cursor.execute(query_liberar_horario, (cita['horario_id'],))
            
            # Cancelar la cita
            query_cancelar = """
                UPDATE citas 
                SET estado = 'CANCELADA', fecha_actualizacion = CURRENT_TIMESTAMP 
                WHERE id = %s
            """
            cursor.execute(query_cancelar, (cita_id,))
            
            mysql.connection.commit()
            cursor.close()
            
            print(f"Cita {cita_id} cancelada exitosamente")
            return {'success': True, 'message': 'Cita cancelada exitosamente'}
            
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al cancelar cita: {str(e)}")
            return {'success': False, 'error': f'Error: {str(e)}'}
    
    @classmethod
    def obtener_cita(cls, mysql, cita_id):
        """Obtiene una cita por ID con información completa"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT c.*, 
                       pac.nombres as paciente_nombres, pac.apellidos as paciente_apellidos,
                       prof.nombres as medico_nombres, prof.apellidos as medico_apellidos,
                       e.nombre as enfermedad_nombre
                FROM citas c
                JOIN pacientes pac ON c.paciente_id = pac.id
                JOIN profesionales prof ON c.medico_id = prof.id
                JOIN enfermedades e ON c.enfermedad_id = e.id
                WHERE c.id = %s
            """
            
            cursor.execute(query, (cita_id,))
            cita = cursor.fetchone()
            cursor.close()
            
            if not cita:
                return {'success': False, 'error': 'Cita no encontrada'}
            
            return {'success': True, 'cita': cita}
            
        except Exception as e:
            print(f"Error al obtener cita: {str(e)}")
            return {'success': False, 'error': f'Error: {str(e)}'}
    
    @classmethod
    def obtener_citas_hoy(cls, mysql):
        """Obtiene citas agendadas para el día actual"""
        try:
            cursor = mysql.connection.cursor()
            hoy = date.today()
            
            query = """
                SELECT c.*, 
                       pac.nombres as paciente_nombres, pac.apellidos as paciente_apellidos,
                       prof.nombres as medico_nombres, prof.apellidos as medico_apellidos,
                       e.nombre as enfermedad_nombre
                FROM citas c
                JOIN pacientes pac ON c.paciente_id = pac.id
                JOIN profesionales prof ON c.medico_id = prof.id
                JOIN enfermedades e ON c.enfermedad_id = e.id
                WHERE c.fecha_cita = %s
                ORDER BY c.hora_inicio ASC
            """
            
            cursor.execute(query, (hoy,))
            citas = cursor.fetchall()
            cursor.close()
            
            return citas
            
        except Exception as e:
            print(f"Error al obtener citas de hoy: {str(e)}")
            return []
    
    @classmethod
    def obtener_citas_por_horario(cls, mysql, horario_id):
        """Obtiene todas las citas asociadas a un horario específico"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT c.*, 
                       pac.nombres as paciente_nombres, pac.apellidos as paciente_apellidos,
                       prof.nombres as medico_nombres, prof.apellidos as medico_apellidos
                FROM citas c
                JOIN pacientes pac ON c.paciente_id = pac.id
                JOIN profesionales prof ON c.medico_id = prof.id
                WHERE c.horario_id = %s
                ORDER BY c.fecha_creacion DESC
            """
            
            cursor.execute(query, (horario_id,))
            citas = cursor.fetchall()
            cursor.close()
            
            return citas
            
        except Exception as e:
            print(f"Error al obtener citas por horario: {str(e)}")
            return []
    
    @classmethod
    def obtener_citas_activas_por_horario(cls, mysql, horario_id):
        """Obtiene solo las citas agendadas (no canceladas) de un horario"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT c.*, 
                       pac.nombres as paciente_nombres, pac.apellidos as paciente_apellidos,
                       prof.nombres as medico_nombres, prof.apellidos as medico_apellidos
                FROM citas c
                JOIN pacientes pac ON c.paciente_id = pac.id
                JOIN profesionales prof ON c.medico_id = prof.id
                WHERE c.horario_id = %s AND c.estado = 'AGENDADA'
                ORDER BY c.fecha_cita, c.hora_inicio
            """
            
            cursor.execute(query, (horario_id,))
            citas = cursor.fetchall()
            cursor.close()
            
            return citas
            
        except Exception as e:
            print(f"Error al obtener citas activas por horario: {str(e)}")
            return []
    
    @classmethod
    def obtener_citas_por_paciente(cls, mysql, paciente_id, estado=None):
        """Obtiene citas de un paciente específico"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT c.*, 
                       prof.nombres as medico_nombres, prof.apellidos as medico_apellidos,
                       prof.especialidad, e.nombre as enfermedad_nombre
                FROM citas c
                JOIN profesionales prof ON c.medico_id = prof.id
                JOIN enfermedades e ON c.enfermedad_id = e.id
                WHERE c.paciente_id = %s
            """
            params = [paciente_id]
            
            if estado:
                query += " AND c.estado = %s"
                params.append(estado)
            
            query += " ORDER BY c.fecha_cita DESC, c.hora_inicio DESC"
            
            cursor.execute(query, params)
            citas = cursor.fetchall()
            cursor.close()
            
            return citas
            
        except Exception as e:
            print(f"Error al obtener citas por paciente: {str(e)}")
            return []
    
    @classmethod
    def obtener_citas_por_medico(cls, mysql, medico_id, fecha_desde=None, fecha_hasta=None):
        """Obtiene citas de un médico específico"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT c.*, 
                       pac.nombres as paciente_nombres, pac.apellidos as paciente_apellidos,
                       e.nombre as enfermedad_nombre
                FROM citas c
                JOIN pacientes pac ON c.paciente_id = pac.id
                JOIN enfermedades e ON c.enfermedad_id = e.id
                WHERE c.medico_id = %s
            """
            params = [medico_id]
            
            if fecha_desde:
                query += " AND c.fecha_cita >= %s"
                params.append(fecha_desde)
            
            if fecha_hasta:
                query += " AND c.fecha_cita <= %s"
                params.append(fecha_hasta)
            
            query += " ORDER BY c.fecha_cita DESC, c.hora_inicio DESC"
            
            cursor.execute(query, params)
            citas = cursor.fetchall()
            cursor.close()
            
            return citas
            
        except Exception as e:
            print(f"Error al obtener citas por médico: {str(e)}")
            return []
    
    @classmethod
    def actualizar_estado_cita(cls, mysql, cita_id, nuevo_estado, observaciones=None):
        """Actualiza el estado de una cita"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                UPDATE citas 
                SET estado = %s, fecha_actualizacion = CURRENT_TIMESTAMP
            """
            params = [nuevo_estado]
            
            if observaciones:
                query += ", observaciones = %s"
                params.append(observaciones)
            
            query += " WHERE id = %s"
            params.append(cita_id)
            
            cursor.execute(query, params)
            
            if cursor.rowcount == 0:
                cursor.close()
                return {'success': False, 'error': 'Cita no encontrada'}
            
            mysql.connection.commit()
            cursor.close()
            
            print(f"Estado de cita {cita_id} actualizado a {nuevo_estado}")
            return {'success': True, 'message': f'Estado actualizado a {nuevo_estado}'}
            
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al actualizar estado de cita: {str(e)}")
            return {'success': False, 'error': f'Error: {str(e)}'}

   
    @staticmethod
    def formatear_duracion(duracion_minutos):
        """Retorna la duración de la cita en formato legible"""
        if duracion_minutos >= 60:
            horas = duracion_minutos // 60
            minutos = duracion_minutos % 60
            if minutos > 0:
                return f"{horas}h {minutos}min"
            return f"{horas}h"
        return f"{duracion_minutos}min"
    
    @staticmethod
    def formatear_horario_completo(hora_inicio, hora_fin):
        """Retorna el horario completo de la cita en formato legible"""
        if isinstance(hora_inicio, str):
            return f"{hora_inicio} - {hora_fin}"
        else:
            return f"{hora_inicio.strftime('%H:%M')} - {hora_fin.strftime('%H:%M')}"
    
    @staticmethod
    def informacion_cita(cita_data):
        """Convierte los datos de cita a formato estructurado"""
        return {
            'id': cita_data['id'],
            'paciente_id': cita_data['paciente_id'],
            'medico_id': cita_data['medico_id'],
            'horario_id': cita_data['horario_id'],
            'enfermedad_id': cita_data['enfermedad_id'],
            'fecha_cita': cita_data['fecha_cita'].isoformat() if isinstance(cita_data['fecha_cita'], date) else str(cita_data['fecha_cita']),
            'hora_inicio': cita_data['hora_inicio'].strftime('%H:%M') if hasattr(cita_data['hora_inicio'], 'strftime') else str(cita_data['hora_inicio']),
            'hora_fin': cita_data['hora_fin'].strftime('%H:%M') if hasattr(cita_data['hora_fin'], 'strftime') else str(cita_data['hora_fin']),
            'duracion_minutos': cita_data['duracion_minutos'],
            'tipo': cita_data['tipo'],
            'consultorio': cita_data['consultorio'],
            'especialidad': cita_data['especialidad'],
            'estado': cita_data['estado'],
            'motivo_consulta': cita_data['motivo_consulta'],
            'observaciones': cita_data['observaciones'],
            'enlace_virtual': cita_data['enlace_virtual'],
            'paciente_nombre': cita_data.get('paciente_nombres', '') + ' ' + cita_data.get('paciente_apellidos', ''),
            'medico_nombre': cita_data.get('medico_nombres', '') + ' ' + cita_data.get('medico_apellidos', ''),
            'enfermedad_nombre': cita_data.get('enfermedad_nombre', '')
        }