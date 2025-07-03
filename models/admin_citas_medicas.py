# models/admin_citas_medicas.py

from datetime import date, datetime

class AdminCitasMedicas:
    """
    Clase para manejar las operaciones de citas médicas desde el panel de administración.
    """
    
    @staticmethod
    def obtener_todas_citas(mysql):
        """
        Obtiene todas las citas con información completa.
        
        Returns:
            list: Lista de citas con relaciones cargadas
        """
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT c.*, 
                       pac.nombres as paciente_nombres, pac.apellidos as paciente_apellidos, pac.dni as paciente_dni,
                       prof.nombres as medico_nombres, prof.apellidos as medico_apellidos,
                       e.nombre as enfermedad_nombre
                FROM citas c
                JOIN pacientes pac ON c.paciente_id = pac.id
                JOIN profesionales prof ON c.medico_id = prof.id
                JOIN enfermedades e ON c.enfermedad_id = e.id
                ORDER BY c.fecha_cita DESC, c.hora_inicio DESC
            """
            
            cursor.execute(query)
            citas = cursor.fetchall()
            cursor.close()
            
            return citas
            
        except Exception as e:
            print(f"Error al obtener todas las citas: {str(e)}")
            return []
    
    @staticmethod
    def obtener_citas_con_filtros(mysql, fecha=None, medico_id=None, especialidad=None, 
                                 estado=None, tipo=None, busqueda=None, 
                                 page=1, per_page=10):
        """
        Obtiene citas con filtros aplicados y paginación.
        
        Args:
            mysql: Instancia de MySQL de Flask-MySQLdb
            fecha (str, optional): Fecha específica en formato YYYY-MM-DD
            medico_id (int, optional): ID del médico
            especialidad (str, optional): Especialidad médica
            estado (str, optional): Estado de la cita
            tipo (str, optional): Tipo de cita (PRESENCIAL/VIRTUAL)
            busqueda (str, optional): Término de búsqueda en nombre del paciente
            page (int): Página actual
            per_page (int): Citas por página
            
        Returns:
            dict: Diccionario con citas paginadas y metadatos
        """
        try:
            cursor = mysql.connection.cursor()
            
            # Construir query base
            query = """
                SELECT c.*, 
                       pac.nombres as paciente_nombres, pac.apellidos as paciente_apellidos, pac.dni as paciente_dni,
                       prof.nombres as medico_nombres, prof.apellidos as medico_apellidos,
                       e.nombre as enfermedad_nombre
                FROM citas c
                JOIN pacientes pac ON c.paciente_id = pac.id
                JOIN profesionales prof ON c.medico_id = prof.id
                JOIN enfermedades e ON c.enfermedad_id = e.id
                WHERE 1=1
            """
            params = []
            
            # Filtro por fecha
            if fecha and fecha != 'todas':
                try:
                    fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
                    query += " AND c.fecha_cita = %s"
                    params.append(fecha_obj)
                except ValueError:
                    pass
            
            # Filtro por médico
            if medico_id and medico_id != 'todos':
                query += " AND c.medico_id = %s"
                params.append(medico_id)
            
            # Filtro por especialidad
            if especialidad and especialidad != 'todas':
                especialidad_map = {
                    'cardiologia': 'CARDIOLOGÍA',
                    'medicina-interna': 'MEDICINA INTERNA',
                    'endocrinologia': 'ENDOCRINOLOGÍA',
                    'psicologia': 'PSICOLOGÍA CLÍNICA',
                    'neumologia': 'NEUMOLOGÍA'
                }
                especialidad_db = especialidad_map.get(especialidad)
                if especialidad_db:
                    query += " AND prof.especialidad = %s"
                    params.append(especialidad_db)
            
            # Filtro por estado
            if estado and estado != 'todos':
                estado_map = {
                    'agendada': 'AGENDADA',
                    'atendida': 'ATENDIDA',
                    'no-atendida': 'NO_ATENDIDA',
                    'cancelada': 'CANCELADA'
                }
                estado_db = estado_map.get(estado)
                if estado_db:
                    query += " AND c.estado = %s"
                    params.append(estado_db)
            
            # Filtro por tipo
            if tipo and tipo != 'todos':
                tipo_db = tipo.upper()
                query += " AND c.tipo = %s"
                params.append(tipo_db)
            
            # Filtro de búsqueda (nombre del paciente)
            if busqueda:
                query += " AND (pac.nombres LIKE %s OR pac.apellidos LIKE %s OR pac.dni LIKE %s)"
                busqueda_like = f"%{busqueda}%"
                params.extend([busqueda_like, busqueda_like, busqueda_like])
            
            # Contar total de registros
            count_query = query.replace(
                "SELECT c.*, pac.nombres as paciente_nombres, pac.apellidos as paciente_apellidos, pac.dni as paciente_dni, prof.nombres as medico_nombres, prof.apellidos as medico_apellidos, e.nombre as enfermedad_nombre",
                "SELECT COUNT(*)"
            )
            cursor.execute(count_query, params)
            total = cursor.fetchone()['COUNT(*)']
            
            # Aplicar ordenamiento y paginación
            query += " ORDER BY c.fecha_cita DESC, c.hora_inicio DESC"
            offset = (page - 1) * per_page
            query += " LIMIT %s OFFSET %s"
            params.extend([per_page, offset])
            
            cursor.execute(query, params)
            citas = cursor.fetchall()
            
            # Formatear datos para el frontend
            citas_formateadas = []
            for cita in citas:
                # Formatear horario completo
                horario_completo = f"{cita['hora_inicio']} - {cita['hora_fin']}"
                if hasattr(cita['hora_inicio'], 'strftime'):
                    horario_completo = f"{cita['hora_inicio'].strftime('%H:%M')} - {cita['hora_fin'].strftime('%H:%M')}"
                
                # Formatear duración
                duracion_formateada = f"{cita['duracion_minutos']}min"
                if cita['duracion_minutos'] >= 60:
                    horas = cita['duracion_minutos'] // 60
                    minutos = cita['duracion_minutos'] % 60
                    if minutos > 0:
                        duracion_formateada = f"{horas}h {minutos}min"
                    else:
                        duracion_formateada = f"{horas}h"
                
                citas_formateadas.append({
                    'id': cita['id'],
                    'paciente': {
                        'id': cita['paciente_id'],
                        'nombre_completo': f"{cita['paciente_nombres']} {cita['paciente_apellidos']}",
                        'dni': cita['paciente_dni']
                    },
                    'medico': {
                        'id': cita['medico_id'],
                        'nombre_completo': f"Dr. {cita['medico_nombres']} {cita['medico_apellidos']}",
                        'especialidad': cita['especialidad']
                    },
                    'fecha_cita': cita['fecha_cita'].strftime('%d/%m/%Y') if hasattr(cita['fecha_cita'], 'strftime') else str(cita['fecha_cita']),
                    'fecha_cita_iso': cita['fecha_cita'].isoformat() if hasattr(cita['fecha_cita'], 'isoformat') else str(cita['fecha_cita']),
                    'hora_inicio': cita['hora_inicio'].strftime('%H:%M') if hasattr(cita['hora_inicio'], 'strftime') else str(cita['hora_inicio']),
                    'hora_fin': cita['hora_fin'].strftime('%H:%M') if hasattr(cita['hora_fin'], 'strftime') else str(cita['hora_fin']),
                    'horario_completo': horario_completo,
                    'duracion_formateada': duracion_formateada,
                    'tipo': cita['tipo'],
                    'estado': cita['estado'],
                    'especialidad': cita['especialidad'],
                    'consultorio': cita.get('consultorio'),
                    'enlace_virtual': cita.get('enlace_virtual'),
                    'motivo_consulta': cita.get('motivo_consulta'),
                    'observaciones': cita.get('observaciones'),
                    'enfermedad_nombre': cita['enfermedad_nombre']
                })
            
            cursor.close()
            
            return {
                'success': True,
                'citas': citas_formateadas,
                'pagination': {
                    'page': page,
                    'pages': (total + per_page - 1) // per_page,
                    'per_page': per_page,
                    'total': total,
                    'has_next': page < ((total + per_page - 1) // per_page),
                    'has_prev': page > 1
                }
            }
            
        except Exception as e:
            print(f"Error al obtener citas con filtros: {str(e)}")
            return {
                'success': False,
                'error': f'Error al obtener citas: {str(e)}',
                'citas': [],
                'pagination': {}
            }
    
    @staticmethod
    def obtener_estadisticas_citas(mysql):
        """
        Obtiene estadísticas generales de las citas.
        
        Returns:
            dict: Estadísticas de citas
        """
        try:
            cursor = mysql.connection.cursor()
            hoy = date.today()
            
            # Total de citas
            cursor.execute("SELECT COUNT(*) as total FROM citas")
            total_citas = cursor.fetchone()['total']
            
            # Citas de hoy
            cursor.execute("SELECT COUNT(*) as total FROM citas WHERE fecha_cita = %s", (hoy,))
            citas_hoy = cursor.fetchone()['total']
            
            # Citas por estado
            cursor.execute("SELECT COUNT(*) as total FROM citas WHERE estado = 'AGENDADA'")
            citas_agendadas = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM citas WHERE estado = 'ATENDIDA'")
            citas_atendidas = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM citas WHERE estado = 'CANCELADA'")
            citas_canceladas = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM citas WHERE estado = 'NO_ATENDIDA'")
            citas_no_atendidas = cursor.fetchone()['total']
            
            # Citas por tipo
            cursor.execute("SELECT COUNT(*) as total FROM citas WHERE tipo = 'PRESENCIAL'")
            citas_presenciales = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM citas WHERE tipo = 'VIRTUAL'")
            citas_virtuales = cursor.fetchone()['total']
            
            # Estadísticas por especialidad
            cursor.execute("""
                SELECT especialidad, COUNT(*) as count 
                FROM citas 
                GROUP BY especialidad
            """)
            especialidades_result = cursor.fetchall()
            stats_especialidad = {row['especialidad']: row['count'] for row in especialidades_result}
            
            cursor.close()
            
            return {
                'total_citas': total_citas,
                'citas_hoy': citas_hoy,
                'por_estado': {
                    'agendadas': citas_agendadas,
                    'atendidas': citas_atendidas,
                    'canceladas': citas_canceladas,
                    'no_atendidas': citas_no_atendidas
                },
                'por_tipo': {
                    'presenciales': citas_presenciales,
                    'virtuales': citas_virtuales
                },
                'por_especialidad': stats_especialidad
            }
            
        except Exception as e:
            print(f"Error al obtener estadísticas de citas: {str(e)}")
            return {
                'error': f'Error al obtener estadísticas: {str(e)}'
            }
    
    @staticmethod
    def obtener_citas_hoy(mysql):
        """
        Obtiene las citas programadas para hoy.
        
        Returns:
            list: Lista de citas de hoy con información completa
        """
        try:
            cursor = mysql.connection.cursor()
            hoy = date.today()
            
            query = """
                SELECT c.*, 
                       pac.nombres as paciente_nombres, pac.apellidos as paciente_apellidos,
                       prof.nombres as medico_nombres, prof.apellidos as medico_apellidos
                FROM citas c
                JOIN pacientes pac ON c.paciente_id = pac.id
                JOIN profesionales prof ON c.medico_id = prof.id
                WHERE c.fecha_cita = %s
                ORDER BY c.hora_inicio ASC
            """
            
            cursor.execute(query, (hoy,))
            citas_hoy = cursor.fetchall()
            cursor.close()
            
            citas_formateadas = []
            for cita in citas_hoy:
                citas_formateadas.append({
                    'id': cita['id'],
                    'paciente_nombre': f"{cita['paciente_nombres']} {cita['paciente_apellidos']}",
                    'medico_nombre': f"Dr. {cita['medico_nombres']} {cita['medico_apellidos']}",
                    'especialidad': cita['especialidad'],
                    'hora_inicio': cita['hora_inicio'].strftime('%H:%M') if hasattr(cita['hora_inicio'], 'strftime') else str(cita['hora_inicio']),
                    'hora_fin': cita['hora_fin'].strftime('%H:%M') if hasattr(cita['hora_fin'], 'strftime') else str(cita['hora_fin']),
                    'tipo': cita['tipo'],
                    'estado': cita['estado'],
                    'consultorio': cita.get('consultorio'),
                    'enlace_virtual': cita.get('enlace_virtual')
                })
            
            return citas_formateadas
            
        except Exception as e:
            print(f"Error en obtener_citas_hoy: {str(e)}")
            return []