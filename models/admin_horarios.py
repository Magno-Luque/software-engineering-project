# models/admin_horarios.py

from datetime import datetime, date, time, timedelta

class HorarioDisponible:
    """Modelo para la tabla horarios_disponibles usando Flask-MySQLdb"""
    
    def __init__(self, mysql):
        self.mysql = mysql
    
    @classmethod
    def obtener_horarios_semana(cls, mysql, fecha_inicio, fecha_fin):
        """Obtiene horarios activos de una semana específica"""
        try:
            cursor = mysql.connection.cursor()
            query = """
                SELECT h.*, p.nombres, p.apellidos, p.especialidad 
                FROM horarios_disponibles h
                JOIN profesionales p ON h.medico_id = p.id
                WHERE h.fecha >= %s AND h.fecha <= %s 
                AND h.estado = 'ACTIVO'
                AND p.estado = 'ACTIVO'
                ORDER BY h.fecha, h.hora_inicio
            """
            cursor.execute(query, (fecha_inicio, fecha_fin))
            horarios = cursor.fetchall()
            cursor.close()
            return horarios
        except Exception as e:
            print(f"Error al obtener horarios de la semana: {str(e)}")
            return []
    
    @classmethod
    def verificar_conflicto_horario(cls, mysql, medico_id, fecha, hora_inicio, hora_fin, excluir_id=None):
        """Verifica si existe conflicto de horarios para un médico"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT id FROM horarios_disponibles 
                WHERE medico_id = %s AND fecha = %s 
                AND estado = 'ACTIVO'
                AND (
                    (hora_inicio <= %s AND hora_fin > %s) OR
                    (hora_inicio < %s AND hora_fin >= %s) OR
                    (hora_inicio >= %s AND hora_fin <= %s)
                )
            """
            params = [medico_id, fecha, hora_inicio, hora_inicio, hora_fin, hora_fin, hora_inicio, hora_fin]
            
            if excluir_id:
                query += " AND id != %s"
                params.append(excluir_id)
            
            cursor.execute(query, params)
            conflicto = cursor.fetchone()
            cursor.close()
            
            return conflicto is not None
            
        except Exception as e:
            print(f"Error al verificar conflicto de horario: {str(e)}")
            return True  # Por seguridad, asumir que hay conflicto si hay error
    
    @classmethod
    def crear_horario(cls, mysql, datos_horario):
        """Crea un nuevo horario disponible en la base de datos"""
        try:
            # Validaciones básicas
            if not datos_horario.get('medico_id'):
                raise ValueError('ID de médico es requerido')
            
            # Convertir strings a objetos date/time si es necesario
            if isinstance(datos_horario['fecha'], str):
                fecha = datetime.strptime(datos_horario['fecha'], '%Y-%m-%d').date()
            else:
                fecha = datos_horario['fecha']
                
            if isinstance(datos_horario['hora_inicio'], str):
                hora_inicio = datetime.strptime(datos_horario['hora_inicio'], '%H:%M').time()
            else:
                hora_inicio = datos_horario['hora_inicio']
                
            if isinstance(datos_horario['hora_fin'], str):
                hora_fin = datetime.strptime(datos_horario['hora_fin'], '%H:%M').time()
            else:
                hora_fin = datos_horario['hora_fin']
            
            if hora_fin <= hora_inicio:
                raise ValueError('La hora de fin debe ser posterior a la hora de inicio')
            
            # Verificar conflictos
            if cls.verificar_conflicto_horario(mysql, datos_horario['medico_id'], fecha, hora_inicio, hora_fin):
                raise ValueError('Ya existe un horario en conflicto para este médico en ese horario')
            
            cursor = mysql.connection.cursor()
            
            query = """
                INSERT INTO horarios_disponibles 
                (medico_id, fecha, hora_inicio, hora_fin, tipo, consultorio, duracion_cita, observaciones, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                datos_horario['medico_id'],
                fecha,
                hora_inicio,
                hora_fin,
                datos_horario.get('tipo', 'PRESENCIAL'),
                datos_horario.get('consultorio'),
                datos_horario.get('duracion_cita', 60),
                datos_horario.get('observaciones'),
                'ACTIVO'
            ))
            
            mysql.connection.commit()
            horario_id = cursor.lastrowid
            cursor.close()
            
            print(f"Horario creado exitosamente con ID: {horario_id}")
            return horario_id
            
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al crear horario: {str(e)}")
            raise
    
    @classmethod
    def obtener_por_id(cls, mysql, horario_id):
        """Obtiene un horario específico por su ID"""
        try:
            cursor = mysql.connection.cursor()
            query = """
                SELECT h.*, p.nombres, p.apellidos, p.especialidad 
                FROM horarios_disponibles h
                JOIN profesionales p ON h.medico_id = p.id
                WHERE h.id = %s
            """
            cursor.execute(query, (horario_id,))
            horario = cursor.fetchone()
            cursor.close()
            return horario
        except Exception as e:
            print(f"Error al obtener horario por ID: {str(e)}")
            return None
    
    @classmethod
    def eliminar_horario(cls, mysql, horario_id):
        """Elimina un horario disponible de la base de datos"""
        try:
            # Verificar citas agendadas
            cursor = mysql.connection.cursor()
            
            query_verificar = """
                SELECT COUNT(*) as citas_activas 
                FROM citas 
                WHERE horario_id = %s AND estado = 'AGENDADA'
            """
            cursor.execute(query_verificar, (horario_id,))
            resultado = cursor.fetchone()
            
            if resultado['citas_activas'] > 0:
                cursor.close()
                raise ValueError(f'No se puede eliminar: tiene {resultado["citas_activas"]} cita(s) agendada(s)')
            
            # Eliminar horario
            query_eliminar = "DELETE FROM horarios_disponibles WHERE id = %s"
            cursor.execute(query_eliminar, (horario_id,))
            
            if cursor.rowcount == 0:
                cursor.close()
                return False
            
            mysql.connection.commit()
            cursor.close()
            
            print(f"Horario {horario_id} eliminado exitosamente")
            return True
            
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al eliminar horario: {str(e)}")
            raise
    
    @classmethod
    def actualizar_horario(cls, mysql, horario_id, datos_horario):
        """Actualiza un horario disponible existente"""
        try:
            # Convertir strings a objetos date/time si es necesario
            if isinstance(datos_horario['fecha'], str):
                fecha = datetime.strptime(datos_horario['fecha'], '%Y-%m-%d').date()
            else:
                fecha = datos_horario['fecha']
                
            if isinstance(datos_horario['hora_inicio'], str):
                hora_inicio = datetime.strptime(datos_horario['hora_inicio'], '%H:%M').time()
            else:
                hora_inicio = datos_horario['hora_inicio']
                
            if isinstance(datos_horario['hora_fin'], str):
                hora_fin = datetime.strptime(datos_horario['hora_fin'], '%H:%M').time()
            else:
                hora_fin = datos_horario['hora_fin']
            
            if hora_fin <= hora_inicio:
                raise ValueError('La hora de fin debe ser posterior a la hora de inicio')
            
            # Verificar conflictos (excluyendo el horario actual)
            if cls.verificar_conflicto_horario(mysql, datos_horario['medico_id'], fecha, hora_inicio, hora_fin, horario_id):
                raise ValueError('Ya existe un horario en conflicto para este médico en ese horario')
            
            cursor = mysql.connection.cursor()
            
            query = """
                UPDATE horarios_disponibles 
                SET medico_id = %s, fecha = %s, hora_inicio = %s, hora_fin = %s, 
                    tipo = %s, consultorio = %s, duracion_cita = %s, observaciones = %s,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            cursor.execute(query, (
                datos_horario['medico_id'],
                fecha,
                hora_inicio,
                hora_fin,
                datos_horario.get('tipo', 'PRESENCIAL'),
                datos_horario.get('consultorio'),
                datos_horario.get('duracion_cita', 60),
                datos_horario.get('observaciones'),
                horario_id
            ))
            
            if cursor.rowcount == 0:
                cursor.close()
                raise ValueError('Horario no encontrado')
            
            mysql.connection.commit()
            cursor.close()
            
            print(f"Horario {horario_id} actualizado exitosamente")
            return True
            
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al actualizar horario: {str(e)}")
            raise
    
    @classmethod
    def crear_horarios_rango(cls, mysql, datos_horario):
        """Crea múltiples slots de 1 hora a partir de un rango"""
        try:
            # Validaciones básicas
            if not datos_horario.get('medico_id'):
                raise ValueError('ID de médico es requerido')
            
            # Convertir strings a objetos date/time 
            if isinstance(datos_horario['fecha'], str):
                fecha = datetime.strptime(datos_horario['fecha'], '%Y-%m-%d').date()
            else:
                fecha = datos_horario['fecha']
                
            if isinstance(datos_horario['hora_inicio'], str):
                hora_inicio = datetime.strptime(datos_horario['hora_inicio'], '%H:%M').time()
            else:
                hora_inicio = datos_horario['hora_inicio']
                
            if isinstance(datos_horario['hora_fin'], str):
                hora_fin = datetime.strptime(datos_horario['hora_fin'], '%H:%M').time()
            else:
                hora_fin = datos_horario['hora_fin']
            
            if hora_fin <= hora_inicio:
                raise ValueError('La hora de fin debe ser posterior a la hora de inicio')
            
            # Generar slots de 1 hora
            slots_creados = []
            hora_actual = datetime.combine(fecha, hora_inicio)
            hora_limite = datetime.combine(fecha, hora_fin)
            
            while hora_actual < hora_limite:
                hora_siguiente = hora_actual + timedelta(hours=1)
                
                # No crear slot si excede el límite
                if hora_siguiente > hora_limite:
                    break
                
                # Verificar conflictos para este slot específico
                if cls.verificar_conflicto_horario(mysql, datos_horario['medico_id'], fecha, hora_actual.time(), hora_siguiente.time()):
                    raise ValueError(f'Conflicto en slot {hora_actual.time().strftime("%H:%M")}-{hora_siguiente.time().strftime("%H:%M")}: ya existe un horario')
                
                # Crear el slot
                slot_datos = datos_horario.copy()
                slot_datos['hora_inicio'] = hora_actual.time()
                slot_datos['hora_fin'] = hora_siguiente.time()
                
                slot_id = cls.crear_horario(mysql, slot_datos)
                slots_creados.append(slot_id)
                
                hora_actual = hora_siguiente
            
            print(f"Se crearon {len(slots_creados)} slots exitosamente")
            return slots_creados
            
        except Exception as e:
            print(f"Error al crear horarios en rango: {str(e)}")
            raise
    
    @classmethod
    def esta_ocupado(cls, mysql, horario_id):
        """Verifica si el horario tiene citas agendadas"""
        try:
            cursor = mysql.connection.cursor()
            query = """
                SELECT COUNT(*) as citas_agendadas 
                FROM citas 
                WHERE horario_id = %s AND estado = 'AGENDADA'
            """
            cursor.execute(query, (horario_id,))
            resultado = cursor.fetchone()
            cursor.close()
            
            return resultado['citas_agendadas'] > 0
            
        except Exception as e:
            print(f"Error al verificar si horario está ocupado: {str(e)}")
            return True  # Por seguridad, asumir que está ocupado
    
    @classmethod
    def obtener_todos_activos(cls, mysql):
        """Obtiene todos los horarios activos"""
        try:
            cursor = mysql.connection.cursor()
            query = """
                SELECT h.*, p.nombres, p.apellidos, p.especialidad 
                FROM horarios_disponibles h
                JOIN profesionales p ON h.medico_id = p.id
                WHERE h.estado = 'ACTIVO'
                ORDER BY h.fecha, h.hora_inicio
            """
            cursor.execute(query)
            horarios = cursor.fetchall()
            cursor.close()
            return horarios
        except Exception as e:
            print(f"Error al obtener horarios activos: {str(e)}")
            return []

class PlantillaHorario:
    """Modelo para la tabla plantillas_horarios usando Flask-MySQLdb"""
    
    def __init__(self, mysql):
        self.mysql = mysql
    
    @classmethod
    def obtener_plantillas_activas_por_medico(cls, mysql, medico_id):
        """Obtiene plantillas activas de un médico específico"""
        try:
            cursor = mysql.connection.cursor()
            query = """
                SELECT pt.*, p.nombres, p.apellidos 
                FROM plantillas_horarios pt
                JOIN profesionales p ON pt.medico_id = p.id
                WHERE pt.medico_id = %s AND pt.activo = 1
                ORDER BY 
                    CASE pt.dia_semana 
                        WHEN 'LUNES' THEN 1
                        WHEN 'MARTES' THEN 2 
                        WHEN 'MIERCOLES' THEN 3
                        WHEN 'JUEVES' THEN 4
                        WHEN 'VIERNES' THEN 5
                        WHEN 'SABADO' THEN 6
                        WHEN 'DOMINGO' THEN 7
                    END
            """
            cursor.execute(query, (medico_id,))
            plantillas = cursor.fetchall()
            cursor.close()
            return plantillas
        except Exception as e:
            print(f"Error al obtener plantillas por médico: {str(e)}")
            return []
    
    @classmethod
    def crear_plantilla(cls, mysql, datos_plantilla):
        """Crea una nueva plantilla de horario"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                INSERT INTO plantillas_horarios 
                (medico_id, dia_semana, hora_inicio, hora_fin, tipo, consultorio, duracion_cita, activo, fecha_inicio, fecha_fin)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                datos_plantilla['medico_id'],
                datos_plantilla['dia_semana'],
                datos_plantilla['hora_inicio'],
                datos_plantilla['hora_fin'],
                datos_plantilla.get('tipo', 'PRESENCIAL'),
                datos_plantilla.get('consultorio'),
                datos_plantilla.get('duracion_cita', 60),
                datos_plantilla.get('activo', True),
                datos_plantilla.get('fecha_inicio'),
                datos_plantilla.get('fecha_fin')
            ))
            
            mysql.connection.commit()
            plantilla_id = cursor.lastrowid
            cursor.close()
            
            print(f"Plantilla creada exitosamente con ID: {plantilla_id}")
            return plantilla_id
            
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al crear plantilla: {str(e)}")
            raise