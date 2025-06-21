# models/admin_citas_medicas.py

from . import db
from sqlalchemy import and_, or_, desc, asc
from datetime import date, datetime
from models.cita import Cita
from models.actores import Paciente, Profesional

class AdminCitasMedicas:
    """
    Clase para manejar las operaciones de citas médicas desde el panel de administración.
    """
    
    @staticmethod
    def obtener_todas_citas():
        """
        Obtiene todas las citas con información completa.
        
        Returns:
            list: Lista de objetos Cita con relaciones cargadas
        """
        return Cita.query.join(
            Paciente, Cita.paciente_id == Paciente.id
        ).join(
            Profesional, Cita.medico_id == Profesional.id
        ).order_by(
            desc(Cita.fecha_cita), 
            desc(Cita.hora_inicio)
        ).all()
    
    @staticmethod
    def obtener_citas_con_filtros(fecha=None, medico_id=None, especialidad=None, 
                                 estado=None, tipo=None, busqueda=None, 
                                 page=1, per_page=10):
        """
        Obtiene citas con filtros aplicados y paginación.
        
        Args:
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
            query = Cita.query.join(
                Paciente, Cita.paciente_id == Paciente.id
            ).join(
                Profesional, Cita.medico_id == Profesional.id
            )
            
            # Filtro por fecha
            if fecha and fecha != 'todas':
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
                query = query.filter(Cita.fecha_cita == fecha_obj)
            
            # Filtro por médico
            if medico_id and medico_id != 'todos':
                query = query.filter(Cita.medico_id == medico_id)
            
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
                    query = query.filter(Profesional.especialidad == especialidad_db)
            
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
                    query = query.filter(Cita.estado == estado_db)
            
            # Filtro por tipo
            if tipo and tipo != 'todos':
                tipo_db = tipo.upper()
                query = query.filter(Cita.tipo == tipo_db)
            
            # Filtro de búsqueda (nombre del paciente)
            if busqueda:
                busqueda_like = f"%{busqueda}%"
                query = query.filter(
                    or_(
                        Paciente.nombres.ilike(busqueda_like),
                        Paciente.apellidos.ilike(busqueda_like),
                        Paciente.dni.like(busqueda_like)
                    )
                )
            
            # Ordenar por fecha y hora más recientes primero
            query = query.order_by(
                desc(Cita.fecha_cita),
                desc(Cita.hora_inicio)
            )
            
            # Aplicar paginación
            citas_paginadas = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            # Formatear datos para el frontend
            citas_formateadas = []
            for cita in citas_paginadas.items:
                paciente = Paciente.query.get(cita.paciente_id)
                profesional = Profesional.query.get(cita.medico_id)
                
                citas_formateadas.append({
                    'id': cita.id,
                    'paciente': {
                        'id': paciente.id,
                        'nombre_completo': paciente.nombre_completo,
                        'dni': paciente.dni
                    },
                    'medico': {
                        'id': profesional.id,
                        'nombre_completo': profesional.nombre_completo,
                        'especialidad': profesional.especialidad
                    },
                    'fecha_cita': cita.fecha_cita.strftime('%d/%m/%Y'),
                    'fecha_cita_iso': cita.fecha_cita.isoformat(),
                    'hora_inicio': cita.hora_inicio.strftime('%H:%M'),
                    'hora_fin': cita.hora_fin.strftime('%H:%M'),
                    'horario_completo': cita.horario_completo,
                    'duracion_formateada': cita.duracion_formateada,
                    'tipo': cita.tipo,
                    'estado': cita.estado,
                    'especialidad': cita.especialidad,
                    'consultorio': cita.consultorio,
                    'enlace_virtual': cita.enlace_virtual,
                    'motivo_consulta': cita.motivo_consulta,
                    'observaciones': cita.observaciones
                })
            
            return {
                'success': True,
                'citas': citas_formateadas,
                'pagination': {
                    'page': citas_paginadas.page,
                    'pages': citas_paginadas.pages,
                    'per_page': citas_paginadas.per_page,
                    'total': citas_paginadas.total,
                    'has_next': citas_paginadas.has_next,
                    'has_prev': citas_paginadas.has_prev
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al obtener citas: {str(e)}',
                'citas': [],
                'pagination': {}
            }
    
    @staticmethod
    def obtener_estadisticas_citas():
        """
        Obtiene estadísticas generales de las citas.
        
        Returns:
            dict: Estadísticas de citas
        """
        try:
            hoy = date.today()
            
            # Total de citas
            total_citas = Cita.query.count()
            
            # Citas de hoy
            citas_hoy = Cita.query.filter(Cita.fecha_cita == hoy).count()
            
            # Citas por estado
            citas_agendadas = Cita.query.filter(Cita.estado == 'AGENDADA').count()
            citas_atendidas = Cita.query.filter(Cita.estado == 'ATENDIDA').count()
            citas_canceladas = Cita.query.filter(Cita.estado == 'CANCELADA').count()
            citas_no_atendidas = Cita.query.filter(Cita.estado == 'NO_ATENDIDA').count()
            
            # Citas por tipo
            citas_presenciales = Cita.query.filter(Cita.tipo == 'PRESENCIAL').count()
            citas_virtuales = Cita.query.filter(Cita.tipo == 'VIRTUAL').count()
            
            # Estadísticas por especialidad
            stats_especialidad = {}
            especialidades = db.session.query(Cita.especialidad).distinct().all()
            for (especialidad,) in especialidades:
                count = Cita.query.filter(Cita.especialidad == especialidad).count()
                stats_especialidad[especialidad] = count
            
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
            return {
                'error': f'Error al obtener estadísticas: {str(e)}'
            }
    
    @staticmethod
    def obtener_citas_hoy():
        """
        Obtiene las citas programadas para hoy.
        
        Returns:
            list: Lista de citas de hoy con información completa
        """
        try:
            hoy = date.today()
            
            citas_hoy = Cita.query.filter(
                Cita.fecha_cita == hoy
            ).join(
                Paciente, Cita.paciente_id == Paciente.id
            ).join(
                Profesional, Cita.medico_id == Profesional.id
            ).order_by(
                asc(Cita.hora_inicio)
            ).all()
            
            citas_formateadas = []
            for cita in citas_hoy:
                paciente = Paciente.query.get(cita.paciente_id)
                profesional = Profesional.query.get(cita.medico_id)
                
                citas_formateadas.append({
                    'id': cita.id,
                    'paciente_nombre': paciente.nombre_completo,
                    'medico_nombre': profesional.nombre_completo,
                    'especialidad': cita.especialidad,
                    'hora_inicio': cita.hora_inicio.strftime('%H:%M'),
                    'hora_fin': cita.hora_fin.strftime('%H:%M'),
                    'tipo': cita.tipo,
                    'estado': cita.estado,
                    'consultorio': cita.consultorio,
                    'enlace_virtual': cita.enlace_virtual
                })
            
            return citas_formateadas
            
        except Exception as e:
            print(f"Error en obtener_citas_hoy: {str(e)}")
            return []