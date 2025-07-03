# models/cita_paciente.py

from datetime import datetime, date, timedelta
import random

class CitaPaciente:
    """Modelo simple para gestión de citas de pacientes"""
    
    @staticmethod
    def obtener_enfermedades_asignadas(mysql, paciente_id):
        """Obtiene las enfermedades asignadas al paciente con sus médicos"""
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                SELECT DISTINCT e.id, e.codigo, e.nombre, e.descripcion, e.especialidad_requerida,
                       pem.medico_id, p.nombres as medico_nombres, p.apellidos as medico_apellidos
                FROM enfermedades e
                JOIN paciente_enfermedad_medico pem ON e.id = pem.enfermedad_id
                JOIN profesionales p ON pem.medico_id = p.id
                WHERE pem.paciente_id = %s 
                AND pem.estado = 'ACTIVO'
                AND e.estado = 'ACTIVO'
                AND p.estado = 'ACTIVO'
                ORDER BY e.nombre
            """, (paciente_id,))
            
            enfermedades = cursor.fetchall()
            print(enfermedades)
            cursor.close()
            
            print(f"Enfermedades encontradas para paciente {paciente_id}: {len(enfermedades)}")
            for e in enfermedades:
                print(f"  - {e['codigo']}: {e['nombre']} (Dr. {e['medico_nombres']} {e['medico_apellidos']})")
            
            return enfermedades
            
        except Exception as e:
            print(f"Error al obtener enfermedades: {str(e)}")
            return []
    
    @staticmethod
    def obtener_horarios_disponibles(mysql, paciente_id, fecha_desde, fecha_hasta, especialidad=None):
        """Obtiene horarios disponibles para el paciente"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT DISTINCT
                    h.id, h.fecha, h.hora_inicio, h.hora_fin, h.tipo, h.consultorio,
                    p.id as medico_id, p.nombres, p.apellidos, p.especialidad,
                    e.id as enfermedad_id, e.codigo as enfermedad_codigo, e.nombre as enfermedad_nombre,
                    e.especialidad_requerida
                FROM horarios_disponibles h
                JOIN profesionales p ON h.medico_id = p.id
                JOIN paciente_enfermedad_medico pem ON p.id = pem.medico_id
                JOIN enfermedades e ON pem.enfermedad_id = e.id
                WHERE pem.paciente_id = %s
                AND pem.estado = 'ACTIVO'
                AND h.estado = 'ACTIVO'
                AND p.estado = 'ACTIVO'
                AND e.estado = 'ACTIVO'
                AND p.especialidad = e.especialidad_requerida
                AND h.fecha >= %s
                AND h.fecha <= %s
            """
            
            params = [paciente_id, fecha_desde, fecha_hasta]
            
            if especialidad and especialidad != 'todas':
                query += " AND p.especialidad = %s"
                params.append(especialidad)
            
            query += " ORDER BY h.fecha, h.hora_inicio"
            
            cursor.execute(query, params)
            horarios = cursor.fetchall()
            cursor.close()
            
            print(f"Horarios encontrados para paciente {paciente_id}: {len(horarios)}")
            
            return horarios
            
        except Exception as e:
            print(f"Error al obtener horarios: {str(e)}")
            return []
    
    @staticmethod
    def crear_cita(mysql, datos_cita):
        """Crea una nueva cita usando la lógica del modelo Cita existente"""
        try:
            cursor = mysql.connection.cursor()
            
            # Verificar que el horario existe y está disponible
            cursor.execute("""
                SELECT * FROM horarios_disponibles 
                WHERE id = %s AND estado = 'ACTIVO'
            """, (datos_cita['horario_id'],))
            
            horario = cursor.fetchone()
            if not horario:
                raise ValueError('El horario no está disponible')
            
            # Verificar asignación médico-paciente-enfermedad
            cursor.execute("""
                SELECT medico_id FROM paciente_enfermedad_medico 
                WHERE paciente_id = %s AND enfermedad_id = %s AND estado = 'ACTIVO'
            """, (datos_cita['paciente_id'], datos_cita['enfermedad_id']))
            
            asignacion = cursor.fetchone()
            
            print(asignacion)
            
            if not asignacion:
                raise ValueError('No hay médico asignado para esta enfermedad')
            
            # Verificar que el médico del horario coincide con el asignado
            if horario['medico_id'] != asignacion['medico_id']:
                raise ValueError('El horario no corresponde al médico asignado para esta enfermedad')
            
            # Obtener datos del médico
            cursor.execute("""
                SELECT nombres, apellidos, especialidad FROM profesionales WHERE id = %s
            """, (asignacion['medico_id'],))
            
            medico = cursor.fetchone()
            if not medico:
                raise ValueError('Médico no encontrado')
            
            # Generar enlace virtual si es necesario
            enlace_virtual = None
            if horario['tipo'] == 'VIRTUAL':
                enlace_virtual = f"https://zoom.us/j/{random.randint(100000000, 999999999)}"
            
            # Crear la cita
            cursor.execute("""
                INSERT INTO citas 
                (paciente_id, medico_id, horario_id, enfermedad_id, fecha_cita, 
                 hora_inicio, hora_fin, duracion_minutos, tipo, consultorio, especialidad, 
                 motivo_consulta, observaciones, enlace_virtual, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                datos_cita['paciente_id'],
                asignacion['medico_id'],
                datos_cita['horario_id'],
                datos_cita['enfermedad_id'],
                horario['fecha'],
                horario['hora_inicio'],
                horario['hora_fin'],
                datos_cita.get('duracion_minutos', 60),
                horario['tipo'],
                horario.get('consultorio'),
                medico['especialidad'],
                datos_cita['motivo_consulta'],
                datos_cita.get('observaciones', ''),
                enlace_virtual,
                'AGENDADA'
            ))
            
            cita_id = cursor.lastrowid
            
            # IMPORTANTE: Marcar horario como INACTIVO
            cursor.execute("""
                UPDATE horarios_disponibles 
                SET estado = 'INACTIVO' 
                WHERE id = %s
            """, (datos_cita['horario_id'],))
            
            mysql.connection.commit()
            cursor.close()
            
            print(f"Cita creada exitosamente con ID: {cita_id}")
            
            return {
                'cita_id': cita_id,
                'detalles': {
                    'fecha': horario['fecha'],
                    'hora_inicio': horario['hora_inicio'],
                    'hora_fin': horario['hora_fin'],
                    'medico': f"Dr. {medico['nombres']} {medico['apellidos']}",
                    'especialidad': medico['especialidad'],
                    'tipo': horario['tipo'],
                    'consultorio': horario.get('consultorio'),
                    'enlace_virtual': enlace_virtual
                }
            }
            
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al crear cita: {str(e)}")
            raise