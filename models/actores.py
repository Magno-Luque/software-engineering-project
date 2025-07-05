# models/actores.py

from datetime import date, datetime
import json
import bcrypt

class Paciente:
    """Modelo para la tabla pacientes usando Flask-MySQLdb"""
    
    def __init__(self, mysql):
        self.mysql = mysql
    
    @classmethod
    def obtener_pacientes_recientes(cls, mysql, limit=5):
        """Obtiene los últimos pacientes registrados"""
        try:
            cursor = mysql.connection.cursor()
            query = """
                SELECT * FROM pacientes 
                ORDER BY fecha_registro DESC 
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            pacientes = cursor.fetchall()
            cursor.close()
            return pacientes
        except Exception as e:
            print(f"Error al obtener pacientes recientes: {str(e)}")
            return []
    
    @classmethod
    def obtener_todos_pacientes(cls, mysql):
        """Obtiene todos los pacientes con sus datos relevantes"""
        try:
            cursor = mysql.connection.cursor()
            query = "SELECT * FROM pacientes ORDER BY fecha_registro DESC"
            cursor.execute(query)
            pacientes = cursor.fetchall()
            cursor.close()
            return pacientes
        except Exception as e:
            print(f"Error al obtener todos los pacientes: {str(e)}")
            return []
    
    @classmethod
    def obtener_por_id(cls, mysql, paciente_id):
        """Obtiene un paciente por su ID"""
        try:
            cursor = mysql.connection.cursor()
            query = "SELECT * FROM pacientes WHERE id = %s"
            cursor.execute(query, (paciente_id,))
            paciente = cursor.fetchone()
            cursor.close()
            return paciente
        except Exception as e:
            print(f"Error al obtener paciente por ID: {str(e)}")
            return None
    
    @classmethod
    def calcular_edad(cls, fecha_nacimiento):
        """Calcula la edad basada en fecha de nacimiento"""
        if fecha_nacimiento:
            hoy = date.today()
            if isinstance(fecha_nacimiento, str):
                fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
            return hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        return None
    
    @classmethod
    def obtener_todos_con_filtros(cls, mysql, estado=None, medico_id=None, fecha_desde=None, fecha_hasta=None, busqueda=None, page=1, per_page=10):
        """Obtiene pacientes con filtros aplicados y paginación"""
        try:
            cursor = mysql.connection.cursor()
            
            # Construir la query base
            query = "SELECT * FROM pacientes WHERE 1=1"
            params = []
            
            # Filtro por estado
            if estado and estado != 'todos':
                query += " AND estado = %s"
                params.append(estado.upper())
            
            # Filtro por médico usando tabla intermedia
            if medico_id and medico_id != 'todos':
                query += """ AND id IN (
                    SELECT paciente_id FROM paciente_enfermedad_medico 
                    WHERE medico_id = %s AND estado = 'ACTIVO'
                )"""
                params.append(medico_id)
            
            # Filtro por rango de fechas
            if fecha_desde:
                query += " AND fecha_registro >= %s"
                params.append(fecha_desde)
            if fecha_hasta:
                query += " AND fecha_registro <= %s"
                params.append(fecha_hasta)
            
            # Filtro de búsqueda
            if busqueda:
                query += " AND (nombres LIKE %s OR apellidos LIKE %s OR dni LIKE %s)"
                busqueda_like = f"%{busqueda}%"
                params.extend([busqueda_like, busqueda_like, busqueda_like])
            
            # Ordenar y paginar
            query += " ORDER BY fecha_registro DESC"
            
            # Calcular offset para paginación
            offset = (page - 1) * per_page
            query += " LIMIT %s OFFSET %s"
            params.extend([per_page, offset])
            
            cursor.execute(query, params)
            pacientes = cursor.fetchall()
            
            # Obtener total de registros para paginación
            count_query = query.replace("SELECT *", "SELECT COUNT(*)", 1)
            count_query = count_query.split(" ORDER BY")[0]  # Remover ORDER BY y LIMIT
            count_params = params[:-2]  # Remover LIMIT y OFFSET
            
            cursor.execute(count_query, count_params)
            total = cursor.fetchone()['COUNT(*)']
            
            cursor.close()
            
            return {
                'items': pacientes,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            print(f"Error al obtener pacientes con filtros: {str(e)}")
            return {'items': [], 'total': 0, 'page': page, 'per_page': per_page, 'pages': 0}
    
    @classmethod
    def crear_paciente_nuevo(cls, mysql, dni, nombres, apellidos, fecha_nacimiento, email, telefono, direccion, enfermedades, medicos_asignados):
        """Crea un nuevo paciente"""
        try:
            cursor = mysql.connection.cursor()
            
            # 1. Crear usuario asociado (rol = 'paciente')
            nombre_usuario = f"{nombres} {apellidos}"
            primer_nombre = nombres.strip().split()[0]
            password_plano = primer_nombre.lower()
            
            password_hash = bcrypt.hashpw(password_plano.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            query_usuario = """
                INSERT INTO usuarios (usuario, password, rol, activo, correo)
                VALUES (%s, %s, 'paciente', 1, %s)
            """
            cursor.execute(query_usuario, (nombre_usuario, password_hash, email))

            # Obtener el ID del nuevo usuario
            usuarios_id1 = cursor.lastrowid

            # 2. Insertar paciente
            query_paciente = """
                INSERT INTO pacientes (
                    dni, nombres, apellidos, fecha_nacimiento, email, telefono, direccion, 
                    enfermedades, estado, usuarios_id1
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            enfermedades_json = json.dumps(enfermedades) if enfermedades else None

            cursor.execute(query_paciente, (
                dni, nombres, apellidos, fecha_nacimiento, email, telefono,
                direccion, enfermedades_json, 'ACTIVO', usuarios_id1
            ))

            paciente_id = cursor.lastrowid

            # 3. Relacionar enfermedades con médicos
            enfermedad_nombre_a_id = {
                "diabetes": 1,
                "hipertension": 2,
                "asma": 3,
                "cardiovascular": 4
            }
            
            # Procesar asignaciones de médicos
            if "medicina_interna" in medicos_asignados:
                # Caso: Todas las enfermedades -> Un médico de medicina interna
                medico_medicina_interna_id = medicos_asignados["medicina_interna"]
                
                for enfermedad_nombre in enfermedades:
                    enfermedad_id = enfermedad_nombre_a_id.get(enfermedad_nombre)
                    if enfermedad_id:
                        query_relacion = """
                            INSERT INTO paciente_enfermedad_medico (paciente_id, enfermedad_id, medico_id, estado)
                            VALUES (%s, %s, %s, %s)
                        """
                        cursor.execute(query_relacion, (paciente_id, enfermedad_id, medico_medicina_interna_id, 'ACTIVO'))
            else:
                # Caso: Médicos específicos por enfermedad
                for enfermedad_nombre in enfermedades:
                    enfermedad_id = enfermedad_nombre_a_id.get(enfermedad_nombre)
                    medico_id = medicos_asignados.get(enfermedad_nombre)
                    
                    if enfermedad_id and medico_id:
                        query_relacion = """
                            INSERT INTO paciente_enfermedad_medico (paciente_id, enfermedad_id, medico_id, estado)
                            VALUES (%s, %s, %s, %s)
                        """
                        cursor.execute(query_relacion, (paciente_id, enfermedad_id, medico_id, 'ACTIVO'))
            
            mysql.connection.commit()
            cursor.close()
            
            print(f"Paciente creado exitosamente con ID: {paciente_id}")
            return paciente_id
            
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al crear paciente: {str(e)}")
            raise
    
    @classmethod
    def actualizar_estado(cls, mysql, paciente_id):
        """Cambia el estado del paciente entre ACTIVO/INACTIVO"""
        try:
            cursor = mysql.connection.cursor()
            
            # Obtener estado actual
            query_select = "SELECT estado FROM pacientes WHERE id = %s"
            cursor.execute(query_select, (paciente_id,))
            resultado = cursor.fetchone()
            
            if not resultado:
                cursor.close()
                return None
            
            nuevo_estado = 'INACTIVO' if resultado['estado'] == 'ACTIVO' else 'ACTIVO'
            
            # Actualizar estado
            query_update = "UPDATE pacientes SET estado = %s WHERE id = %s"
            cursor.execute(query_update, (nuevo_estado, paciente_id))
            
            mysql.connection.commit()
            cursor.close()
            
            return nuevo_estado
            
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al actualizar estado del paciente: {str(e)}")
            raise
    
    @classmethod
    def obtener_con_cuidadores(cls, mysql, paciente_id):
        """Obtiene un paciente con sus cuidadores"""
        try:
            cursor = mysql.connection.cursor()
            
            # Obtener paciente
            query_paciente = "SELECT * FROM pacientes WHERE id = %s"
            cursor.execute(query_paciente, (paciente_id,))
            paciente = cursor.fetchone()
            
            if paciente:
                # Obtener cuidadores
                query_cuidadores = "SELECT * FROM cuidadores WHERE paciente_id = %s AND estado = 'ACTIVO'"
                cursor.execute(query_cuidadores, (paciente_id,))
                cuidadores = cursor.fetchall()
                
                paciente['cuidadores'] = cuidadores
            
            cursor.close()
            return paciente
            
        except Exception as e:
            print(f"Error al obtener paciente con cuidadores: {str(e)}")
            return None

class Profesional:
    """Modelo para la tabla profesionales usando Flask-MySQLdb"""
    
    def __init__(self, mysql):
        self.mysql = mysql
    
    @classmethod
    def obtener_medicos_activos(cls, mysql):
        """Obtiene todos los médicos activos para asignación"""
        try:
            cursor = mysql.connection.cursor()
            query = """
                SELECT * FROM profesionales 
                WHERE rol = 'MÉDICO' AND estado = 'ACTIVO'
                ORDER BY nombres, apellidos
            """
            cursor.execute(query)
            medicos = cursor.fetchall()
            cursor.close()
            return medicos
        except Exception as e:
            print(f"Error al obtener médicos activos: {str(e)}")
            return []
    
    @classmethod
    def obtener_por_id(cls, mysql, profesional_id):
        """Obtiene un profesional por su ID"""
        try:
            cursor = mysql.connection.cursor()
            query = "SELECT * FROM profesionales WHERE id = %s"
            cursor.execute(query, (profesional_id,))
            profesional = cursor.fetchone()
            cursor.close()
            return profesional
        except Exception as e:
            print(f"Error al obtener profesional por ID: {str(e)}")
            return None
    
    @classmethod
    def obtener_todos_activos(cls, mysql):
        """Obtiene todos los profesionales activos"""
        try:
            cursor = mysql.connection.cursor()
            query = """
                SELECT * FROM profesionales 
                WHERE estado = 'ACTIVO'
                ORDER BY especialidad, nombres, apellidos
            """
            cursor.execute(query)
            profesionales = cursor.fetchall()
            cursor.close()
            return profesionales
        except Exception as e:
            print(f"Error al obtener profesionales activos: {str(e)}")
            return []
    
    @classmethod
    def obtener_por_especialidad(cls, mysql, especialidad):
        """Obtiene profesionales por especialidad"""
        try:
            cursor = mysql.connection.cursor()
            query = """
                SELECT * FROM profesionales 
                WHERE especialidad = %s AND estado = 'ACTIVO'
                ORDER BY nombres, apellidos
            """
            cursor.execute(query, (especialidad,))
            profesionales = cursor.fetchall()
            cursor.close()
            return profesionales
        except Exception as e:
            print(f"Error al obtener profesionales por especialidad: {str(e)}")
            return []
    
    @classmethod
    def obtener_nombre_completo(cls, profesional_data):
        """Retorna nombre completo del profesional"""
        if profesional_data:
            return f"Dr. {profesional_data['nombres']} {profesional_data['apellidos']}"
        return ""
    
    @classmethod
    def obtener_nombre_formal(cls, profesional_data):
        """Formato estándar para mostrar: 'PrimerNombre PrimerApellido'"""
        if profesional_data:
            primer_nombre = profesional_data['nombres'].split()[0] if profesional_data['nombres'] else ""
            primer_apellido = profesional_data['apellidos'].split()[0] if profesional_data['apellidos'] else ""
            return f"{primer_nombre} {primer_apellido}".strip()
        return ""

class Cuidador:
    """Modelo para la tabla cuidadores usando Flask-MySQLdb"""
    
    def __init__(self, mysql):
        self.mysql = mysql
    
    @classmethod
    def crear_cuidador(cls, mysql, paciente_id, nombre_completo, dni, telefono, relacion_paciente):
        """Crea un nuevo cuidador para un paciente"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                INSERT INTO cuidadores (paciente_id, nombre_completo, dni, telefono, relacion_paciente, estado)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                paciente_id, nombre_completo, dni, telefono, relacion_paciente, 'ACTIVO'
            ))
            
            mysql.connection.commit()
            cuidador_id = cursor.lastrowid
            cursor.close()
            
            print(f"Cuidador creado exitosamente con ID: {cuidador_id}")
            return cuidador_id
            
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al crear cuidador: {str(e)}")
            raise
    
    @classmethod
    def obtener_por_paciente(cls, mysql, paciente_id):
        """Obtiene cuidadores de un paciente específico"""
        try:
            cursor = mysql.connection.cursor()
            query = """
                SELECT * FROM cuidadores 
                WHERE paciente_id = %s AND estado = 'ACTIVO'
                ORDER BY fecha_registro DESC
            """
            cursor.execute(query, (paciente_id,))
            cuidadores = cursor.fetchall()
            cursor.close()
            return cuidadores
        except Exception as e:
            print(f"Error al obtener cuidadores por paciente: {str(e)}")
            return []

class Enfermedad:
    """Modelo para la tabla enfermedades usando Flask-MySQLdb"""
    
    def __init__(self, mysql):
        self.mysql = mysql
    
    @classmethod
    def obtener_todas_activas(cls, mysql):
        """Obtiene todas las enfermedades activas"""
        try:
            cursor = mysql.connection.cursor()
            query = """
                SELECT * FROM enfermedades 
                WHERE estado = 'ACTIVO'
                ORDER BY nombre
            """
            cursor.execute(query)
            enfermedades = cursor.fetchall()
            cursor.close()
            return enfermedades
        except Exception as e:
            print(f"Error al obtener enfermedades activas: {str(e)}")
            return []
    
    @classmethod
    def obtener_por_id(cls, mysql, enfermedad_id):
        """Obtiene una enfermedad por su ID"""
        try:
            cursor = mysql.connection.cursor()
            query = "SELECT * FROM enfermedades WHERE id = %s"
            cursor.execute(query, (enfermedad_id,))
            enfermedad = cursor.fetchone()
            cursor.close()
            return enfermedad
        except Exception as e:
            print(f"Error al obtener enfermedad por ID: {str(e)}")
            return None

class PacienteEnfermedadMedico:
    """Modelo para la tabla paciente_enfermedad_medico usando Flask-MySQLdb"""
    
    def __init__(self, mysql):
        self.mysql = mysql
    
    @classmethod
    def obtener_asignaciones_paciente(cls, mysql, paciente_id):
        """Obtiene las asignaciones médicas de un paciente"""
        try:
            cursor = mysql.connection.cursor()
            query = """
                SELECT pem.*, e.nombre as enfermedad_nombre, e.descripcion as enfermedad_descripcion,
                       p.nombres as medico_nombres, p.apellidos as medico_apellidos, p.especialidad
                FROM paciente_enfermedad_medico pem
                JOIN enfermedades e ON pem.enfermedad_id = e.id
                JOIN profesionales p ON pem.medico_id = p.id
                WHERE pem.paciente_id = %s AND pem.estado = 'ACTIVO'
                ORDER BY e.nombre
            """
            cursor.execute(query, (paciente_id,))
            asignaciones = cursor.fetchall()
            cursor.close()
            return asignaciones
        except Exception as e:
            print(f"Error al obtener asignaciones de paciente: {str(e)}")
            return []
    
    @classmethod
    def crear_asignacion(cls, mysql, paciente_id, enfermedad_id, medico_id, observaciones=None):
        """Crea una nueva asignación paciente-enfermedad-médico"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                INSERT INTO paciente_enfermedad_medico (paciente_id, enfermedad_id, medico_id, estado, observaciones)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                paciente_id, enfermedad_id, medico_id, 'ACTIVO', observaciones
            ))
            
            mysql.connection.commit()
            asignacion_id = cursor.lastrowid
            cursor.close()
            
            print(f"Asignación creada exitosamente con ID: {asignacion_id}")
            return asignacion_id
            
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al crear asignación: {str(e)}")
            raise
    
    @classmethod
    def obtener_pacientes_por_medico(cls, mysql, medico_id):
        """Obtiene pacientes asignados a un médico específico"""
        try:
            cursor = mysql.connection.cursor()
            query = """
                SELECT DISTINCT pac.*, e.nombre as enfermedad_nombre
                FROM pacientes pac
                JOIN paciente_enfermedad_medico pem ON pac.id = pem.paciente_id
                JOIN enfermedades e ON pem.enfermedad_id = e.id
                WHERE pem.medico_id = %s AND pem.estado = 'ACTIVO' AND pac.estado = 'ACTIVO'
                ORDER BY pac.nombres, pac.apellidos
            """
            cursor.execute(query, (medico_id,))
            pacientes = cursor.fetchall()
            cursor.close()
            return pacientes
        except Exception as e:
            print(f"Error al obtener pacientes por médico: {str(e)}")
            return []


class Cita:
    """Modelo para la tabla citas usando Flask-MySQLdb"""
    
    def __init__(self, mysql):
        self.mysql = mysql
    
    @classmethod
    def obtener_citas_por_medico_fecha(cls, mysql, medico_id, fecha=None, estado='todas'):
        """Obtiene las citas de un médico específico en una fecha"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT c.*, 
                       p.nombres as paciente_nombres, p.apellidos as paciente_apellidos,
                       e.nombre as enfermedad_nombre
                FROM citas c
                JOIN pacientes p ON c.paciente_id = p.id
                LEFT JOIN enfermedades e ON c.enfermedad_id = e.id
                WHERE c.medico_id = %s
            """
            params = [medico_id]
            
            # Filtro por fecha
            if fecha:
                query += " AND c.fecha_cita = %s"
                params.append(fecha)
            
            # Filtro por estado
            if estado and estado != 'todas':
                query += " AND c.estado = %s"
                params.append(estado.upper())
            
            query += " ORDER BY c.fecha_cita, c.hora_inicio"
            
            cursor.execute(query, params)
            citas = cursor.fetchall()
            cursor.close()
            
            return citas
            
        except Exception as e:
            print(f"Error al obtener citas por médico y fecha: {str(e)}")
            return []
    
    @classmethod
    def obtener_citas_hoy(cls, mysql, medico_id):
        """Obtiene las citas de hoy de un médico"""
        try:
            from datetime import date
            
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT c.*, 
                       p.nombres as paciente_nombres, p.apellidos as paciente_apellidos,
                       e.nombre as enfermedad_nombre
                FROM citas c
                JOIN pacientes p ON c.paciente_id = p.id
                LEFT JOIN enfermedades e ON c.enfermedad_id = e.id
                WHERE c.medico_id = %s 
                AND c.fecha_cita = CURDATE()
                AND c.estado = 'AGENDADA'
                ORDER BY c.hora_inicio
            """
            
            cursor.execute(query, (medico_id,))
            citas = cursor.fetchall()
            cursor.close()
            
            return citas
            
        except Exception as e:
            print(f"Error al obtener citas de hoy: {str(e)}")
            return []
    
    @classmethod
    def contar_citas_hoy(cls, mysql, medico_id):
        """Cuenta las citas de hoy de un médico"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT COUNT(*) as total
                FROM citas
                WHERE medico_id = %s 
                AND fecha_cita = CURDATE()
                AND estado = 'AGENDADA'
            """
            
            cursor.execute(query, (medico_id,))
            resultado = cursor.fetchone()
            cursor.close()
            
            return resultado['total'] if resultado else 0
            
        except Exception as e:
            print(f"Error al contar citas de hoy: {str(e)}")
            return 0
    
    @classmethod
    def obtener_por_id(cls, mysql, cita_id):
        """Obtiene una cita por su ID"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT c.*, 
                       p.nombres as paciente_nombres, p.apellidos as paciente_apellidos,
                       e.nombre as enfermedad_nombre,
                       prof.nombres as medico_nombres, prof.apellidos as medico_apellidos
                FROM citas c
                JOIN pacientes p ON c.paciente_id = p.id
                LEFT JOIN enfermedades e ON c.enfermedad_id = e.id
                LEFT JOIN profesionales prof ON c.medico_id = prof.id
                WHERE c.id = %s
            """
            
            cursor.execute(query, (cita_id,))
            cita = cursor.fetchone()
            cursor.close()
            
            return cita
            
        except Exception as e:
            print(f"Error al obtener cita por ID: {str(e)}")
            return None
    
    @classmethod
    def actualizar_estado(cls, mysql, cita_id, nuevo_estado, observaciones=None):
        """Actualiza el estado de una cita"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                UPDATE citas 
                SET estado = %s, observaciones = %s, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            cursor.execute(query, (nuevo_estado, observaciones, cita_id))
            mysql.connection.commit()
            cursor.close()
            
            return True
            
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al actualizar estado de cita: {str(e)}")
            return False
    
    @classmethod
    def obtener_proximas_citas(cls, mysql, medico_id, dias=7):
        """Obtiene las próximas citas del médico en los próximos X días"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT c.*, 
                       p.nombres as paciente_nombres, p.apellidos as paciente_apellidos,
                       e.nombre as enfermedad_nombre
                FROM citas c
                JOIN pacientes p ON c.paciente_id = p.id
                LEFT JOIN enfermedades e ON c.enfermedad_id = e.id
                WHERE c.medico_id = %s 
                AND c.fecha_cita BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
                AND c.estado = 'AGENDADA'
                ORDER BY c.fecha_cita, c.hora_inicio
                LIMIT 10
            """
            
            cursor.execute(query, (medico_id, dias))
            citas = cursor.fetchall()
            cursor.close()
            
            return citas
            
        except Exception as e:
            print(f"Error al obtener próximas citas: {str(e)}")
            return []
    
    @classmethod
    def obtener_citas_por_paciente(cls, mysql, paciente_id, estado='todas', limite=10):
        """Obtiene las citas de un paciente específico"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT c.*, 
                       prof.nombres as medico_nombres, prof.apellidos as medico_apellidos,
                       e.nombre as enfermedad_nombre
                FROM citas c
                JOIN profesionales prof ON c.medico_id = prof.id
                LEFT JOIN enfermedades e ON c.enfermedad_id = e.id
                WHERE c.paciente_id = %s
            """
            params = [paciente_id]
            
            # Filtro por estado
            if estado and estado != 'todas':
                query += " AND c.estado = %s"
                params.append(estado.upper())
            
            query += " ORDER BY c.fecha_cita DESC, c.hora_inicio DESC LIMIT %s"
            params.append(limite)
            
            cursor.execute(query, params)
            citas = cursor.fetchall()
            cursor.close()
            
            return citas
            
        except Exception as e:
            print(f"Error al obtener citas por paciente: {str(e)}")
            return []
    
    @classmethod
    def obtener_proximas_citas_paciente(cls, mysql, paciente_id, dias=30, limit=10):
        """Obtiene las próximas citas de un paciente"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT c.*, 
                       prof.nombres as medico_nombres, prof.apellidos as medico_apellidos,
                       e.nombre as enfermedad_nombre
                FROM citas c
                JOIN profesionales prof ON c.medico_id = prof.id
                LEFT JOIN enfermedades e ON c.enfermedad_id = e.id
                WHERE c.paciente_id = %s 
                AND c.fecha_cita >= CURDATE()
                AND c.fecha_cita <= DATE_ADD(CURDATE(), INTERVAL %s DAY)
                AND c.estado = 'AGENDADA'
                ORDER BY c.fecha_cita ASC, c.hora_inicio ASC
                LIMIT %s
            """
            
            cursor.execute(query, (paciente_id, dias, limit))
            citas = cursor.fetchall()
            cursor.close()
            
            return citas
            
        except Exception as e:
            print(f"Error al obtener próximas citas del paciente: {str(e)}")
            return []
    
    @classmethod
    def obtener_citas_hoy_paciente(cls, mysql, paciente_id):
        """Obtiene las citas de hoy de un paciente"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT c.*, 
                       prof.nombres as medico_nombres, prof.apellidos as medico_apellidos,
                       e.nombre as enfermedad_nombre
                FROM citas c
                JOIN profesionales prof ON c.medico_id = prof.id
                LEFT JOIN enfermedades e ON c.enfermedad_id = e.id
                WHERE c.paciente_id = %s 
                AND c.fecha_cita = CURDATE()
                AND c.estado = 'AGENDADA'
                ORDER BY c.hora_inicio ASC
            """
            
            cursor.execute(query, (paciente_id,))
            citas = cursor.fetchall()
            cursor.close()
            
            return citas
            
        except Exception as e:
            print(f"Error al obtener citas de hoy del paciente: {str(e)}")
            return []
    
    @classmethod
    def contar_citas_paciente(cls, mysql, paciente_id):
        """Cuenta el total de citas de un paciente"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT COUNT(*) as total
                FROM citas
                WHERE paciente_id = %s
            """
            
            cursor.execute(query, (paciente_id,))
            resultado = cursor.fetchone()
            cursor.close()
            
            return resultado['total'] if resultado else 0
            
        except Exception as e:
            print(f"Error al contar citas del paciente: {str(e)}")
            return 0
    
    @classmethod
    def contar_citas_pendientes_paciente(cls, mysql, paciente_id):
        """Cuenta las citas pendientes de un paciente"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT COUNT(*) as total
                FROM citas
                WHERE paciente_id = %s 
                AND estado = 'AGENDADA'
                AND fecha_cita >= CURDATE()
            """
            
            cursor.execute(query, (paciente_id,))
            resultado = cursor.fetchone()
            cursor.close()
            
            return resultado['total'] if resultado else 0
            
        except Exception as e:
            print(f"Error al contar citas pendientes del paciente: {str(e)}")
            return 0
    
    @classmethod
    def obtener_ultima_cita_atendida(cls, mysql, paciente_id):
        """Obtiene la última cita atendida del paciente"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT c.*, 
                       prof.nombres as medico_nombres, prof.apellidos as medico_apellidos,
                       e.nombre as enfermedad_nombre
                FROM citas c
                JOIN profesionales prof ON c.medico_id = prof.id
                LEFT JOIN enfermedades e ON c.enfermedad_id = e.id
                WHERE c.paciente_id = %s 
                AND c.estado = 'ATENDIDA'
                ORDER BY c.fecha_cita DESC, c.hora_inicio DESC
                LIMIT 1
            """
            
            cursor.execute(query, (paciente_id,))
            cita = cursor.fetchone()
            cursor.close()
            
            return cita
            
        except Exception as e:
            print(f"Error al obtener última cita atendida: {str(e)}")
            return None

class AlertaCritica:
    """Modelo para la tabla alertas_criticas usando Flask-MySQLdb"""
    
    def __init__(self, mysql):
        self.mysql = mysql
    
    @classmethod
    def obtener_alertas_pendientes(cls, mysql, medico_id=None):
        """Obtiene alertas críticas pendientes"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT ac.*, 
                       p.nombres as paciente_nombres, p.apellidos as paciente_apellidos,
                       e.nombre as enfermedad_nombre
                FROM alertas_criticas ac
                JOIN pacientes p ON ac.paciente_id = p.id
                LEFT JOIN enfermedades e ON ac.enfermedad_relacionada_id = e.id
            """
            params = []
            
            if medico_id:
                query += """
                    WHERE ac.paciente_id IN (
                        SELECT DISTINCT pem.paciente_id 
                        FROM paciente_enfermedad_medico pem 
                        WHERE pem.medico_id = %s AND pem.estado = 'ACTIVO'
                    )
                    AND ac.estado = 'PENDIENTE'
                """
                params.append(medico_id)
            else:
                query += " WHERE ac.estado = 'PENDIENTE'"
            
            query += " ORDER BY ac.fecha_alerta DESC, ac.criticidad DESC"
            
            cursor.execute(query, params)
            alertas = cursor.fetchall()
            cursor.close()
            
            return alertas
            
        except Exception as e:
            print(f"Error al obtener alertas pendientes: {str(e)}")
            return []
    
    @classmethod
    def contar_alertas_pendientes(cls, mysql, medico_id=None):
        """Cuenta las alertas críticas pendientes"""
        try:
            cursor = mysql.connection.cursor()
            
            if medico_id:
                query = """
                    SELECT COUNT(*) as total
                    FROM alertas_criticas ac
                    WHERE ac.paciente_id IN (
                        SELECT DISTINCT pem.paciente_id 
                        FROM paciente_enfermedad_medico pem 
                        WHERE pem.medico_id = %s AND pem.estado = 'ACTIVO'
                    )
                    AND ac.estado = 'PENDIENTE'
                """
                cursor.execute(query, (medico_id,))
            else:
                query = """
                    SELECT COUNT(*) as total
                    FROM alertas_criticas
                    WHERE estado = 'PENDIENTE'
                """
                cursor.execute(query)
            
            resultado = cursor.fetchone()
            cursor.close()
            
            return resultado['total'] if resultado else 0
            
        except Exception as e:
            print(f"Error al contar alertas pendientes: {str(e)}")
            return 0
    
    @classmethod
    def marcar_como_resuelta(cls, mysql, alerta_id, medico_id, observaciones=None):
        """Marca una alerta como resuelta"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                UPDATE alertas_criticas 
                SET estado = 'RESUELTA', 
                    medico_asignado_id = %s,
                    fecha_resolucion = CURRENT_TIMESTAMP,
                    observaciones = %s
                WHERE id = %s
            """
            
            cursor.execute(query, (medico_id, observaciones, alerta_id))
            mysql.connection.commit()
            cursor.close()
            
            return True
            
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al marcar alerta como resuelta: {str(e)}")
            return False
    
    @classmethod
    def obtener_por_paciente(cls, mysql, paciente_id, estado='todas'):
        """Obtiene alertas de un paciente específico"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT ac.*, e.nombre as enfermedad_nombre
                FROM alertas_criticas ac
                LEFT JOIN enfermedades e ON ac.enfermedad_relacionada_id = e.id
                WHERE ac.paciente_id = %s
            """
            params = [paciente_id]
            
            if estado != 'todas':
                query += " AND ac.estado = %s"
                params.append(estado.upper())
            
            query += " ORDER BY ac.fecha_alerta DESC"
            
            cursor.execute(query, params)
            alertas = cursor.fetchall()
            cursor.close()
            
            return alertas
            
        except Exception as e:
            print(f"Error al obtener alertas por paciente: {str(e)}")
            return []

# Agregar estos métodos a la clase Paciente existente:

    @classmethod
    def contar_pacientes_asignados(cls, mysql, medico_id):
        """Cuenta los pacientes asignados a un médico"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT COUNT(DISTINCT pem.paciente_id) as total
                FROM paciente_enfermedad_medico pem
                JOIN pacientes p ON pem.paciente_id = p.id
                WHERE pem.medico_id = %s 
                AND pem.estado = 'ACTIVO'
                AND p.estado = 'ACTIVO'
            """
            
            cursor.execute(query, (medico_id,))
            resultado = cursor.fetchone()
            cursor.close()
            
            return resultado['total'] if resultado else 0
            
        except Exception as e:
            print(f"Error al contar pacientes asignados: {str(e)}")
            return 0
    
    @classmethod
    def obtener_pacientes_alto_riesgo(cls, mysql, medico_id, limit=5):
        """Obtiene pacientes de alto riesgo asignados al médico"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT DISTINCT p.*, COUNT(ac.id) as alertas_criticas
                FROM pacientes p
                JOIN paciente_enfermedad_medico pem ON p.id = pem.paciente_id
                LEFT JOIN alertas_criticas ac ON p.id = ac.paciente_id 
                    AND ac.estado = 'PENDIENTE' 
                    AND ac.criticidad = 'ALTA'
                WHERE pem.medico_id = %s 
                AND pem.estado = 'ACTIVO'
                AND p.estado = 'ACTIVO'
                GROUP BY p.id
                HAVING alertas_criticas > 0
                ORDER BY alertas_criticas DESC, ac.fecha_alerta DESC
                LIMIT %s
            """
            
            cursor.execute(query, (medico_id, limit))
            pacientes = cursor.fetchall()
            cursor.close()
            
            return pacientes
            
        except Exception as e:
            print(f"Error al obtener pacientes de alto riesgo: {str(e)}")
            return []