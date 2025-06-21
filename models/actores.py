# models/actores.py

from . import db
from sqlalchemy import and_, or_, desc, asc
from datetime import date, datetime
import json


# ------------------------------------------------------------------------------
# MODELO: Paciente
# Propósito: Representa pacientes del sistema con datos básicos.
# Relaciones:
#   - Relación 1:N con Cita (definida en modelo Cita)
# ------------------------------------------------------------------------------
class Paciente(db.Model):
    __tablename__ = 'pacientes'
    
    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(8), unique=True, nullable=False)  # 
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    telefono = db.Column(db.String(15))  # 
    email = db.Column(db.String(100))
    direccion = db.Column(db.Text)  # 
    enfermedades = db.Column(db.JSON)  # Lista de enfermedades
    fecha_registro = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())  # 
    estado = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')  #
    
    # REMOVER esta línea (ya no existe en la nueva estructura):
    # medico_asignado_id = db.Column(db.Integer, db.ForeignKey('profesionales.id'))
    
    # RELACIONES CORREGIDAS
    # medico_asignado = db.relationship('Profesional', backref='pacientes_asignados')  # REMOVER
    cuidadores = db.relationship('Cuidador', backref='paciente', cascade='all, delete-orphan')
    
    ######################### admin-dashboard
    # NOTA: La relación con Cita se define en el modelo Cita via backref

    @staticmethod
    def obtener_pacientes_recientes(limit=5):
        """
        Obtiene los últimos pacientes registrados.
        
        Args:
            limit (int): Número máximo de registros a retornar (default: 5)
            
        Returns:
            list: Lista de pacientes ordenados por fecha descendente
        """
        return Paciente.query.order_by(desc(Paciente.fecha_registro)).limit(limit).all()
    
    ####################
    
    ######################### admin-pacientes
    @staticmethod
    def obtener_todos_pacientes():
        """
        Obtiene todos los pacientes con sus datos relevantes.
                
        Returns:
            list: Lista de diccionarios con información estructurada de cada paciente.
        """
        return Paciente.query.all()

    @property
    def nombre_completo(self):
        """Retorna nombre completo del paciente"""
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def edad(self):
        """Calcula la edad basada en fecha de nacimiento"""
        if self.fecha_nacimiento:
            hoy = date.today()
            return hoy.year - self.fecha_nacimiento.year - ((hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        return None
    
    @property
    def enfermedades_lista(self):
        """Retorna lista de enfermedades o lista vacía"""
        return self.enfermedades if self.enfermedades else []
    
    @property
    def tiene_cuidador(self):
        """Verifica si el paciente tiene cuidador asignado"""
        return len(self.cuidadores) > 0
    
    @staticmethod
    def obtener_todos_con_filtros(estado=None, medico_id=None, fecha_desde=None, fecha_hasta=None, busqueda=None, page=1, per_page=10):
        """
        Obtiene pacientes con filtros aplicados y paginación
        """
        query = Paciente.query
        
        # Filtro por estado
        if estado and estado != 'todos':
            query = query.filter(Paciente.estado == estado.upper())
        
        # Filtro por médico asignado
        if medico_id and medico_id != 'todos':
            query = query.filter(Paciente.medico_asignado_id == medico_id)
        
        # Filtro por rango de fechas
        if fecha_desde:
            query = query.filter(Paciente.fecha_registro >= fecha_desde)
        if fecha_hasta:
            query = query.filter(Paciente.fecha_registro <= fecha_hasta)
        
        # Filtro de búsqueda (nombre o DNI)
        if busqueda:
            busqueda_like = f"%{busqueda}%"
            query = query.filter(
                or_(
                    Paciente.nombres.ilike(busqueda_like),
                    Paciente.apellidos.ilike(busqueda_like),
                    Paciente.dni.like(busqueda_like)
                )
            )
        
        # Ordenar por fecha de registro descendente
        query = query.order_by(desc(Paciente.fecha_registro))
        
        # Aplicar paginación
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def crear_paciente(dni, nombres, apellidos, fecha_nacimiento, email, direccion, enfermedades, medico_asignado_id):
        """
        Crea un nuevo paciente
        """
        nuevo_paciente = Paciente(
            dni=dni,
            nombres=nombres,
            apellidos=apellidos,
            fecha_nacimiento=fecha_nacimiento,
            email=email,
            direccion=direccion,
            enfermedades=enfermedades,
            medico_asignado_id=medico_asignado_id
        )
        
        db.session.add(nuevo_paciente)
        db.session.commit()
        return nuevo_paciente
    
    def actualizar_estado(self):
        """
        Cambia el estado del paciente entre ACTIVO/INACTIVO
        """
        self.estado = 'INACTIVO' if self.estado == 'ACTIVO' else 'ACTIVO'
        db.session.commit()
        return self.estado
    
    @staticmethod
    def crear_paciente_nuevo(dni, nombres, apellidos, fecha_nacimiento, email, telefono, direccion, enfermedades, medicos_asignados):
        """
        NUEVO MÉTODO - Crea un nuevo paciente 
        """
        nuevo_paciente = Paciente(
            dni=dni,
            nombres=nombres,
            apellidos=apellidos,
            fecha_nacimiento=fecha_nacimiento,
            email=email,
            telefono=telefono,
            direccion=direccion,
            enfermedades=enfermedades,
            estado='ACTIVO'
        )
        
        db.session.add(nuevo_paciente)
        
        db.session.flush()  # Para obtener el ID del paciente recién creado
        
        enfermedad_nombre_a_id = {
            "diabetes": 1,
            "hipertension": 2,
            "asma": 3,
            "cardiovascular": 4
        }
        
        enfermedad_descripcion = {
            1: "Diabetes",
            2: "Hipertensión", 
            3: "Asma",
            4: "Cardiovascular"
        }
        
        # Ahora registramos cada enfermedad en la tabla intermedia
        # Procesar asignaciones de médicos
        if "medicina_interna" in medicos_asignados:
            # Caso: Todas las enfermedades -> Un médico de medicina interna
            medico_medicina_interna_id = medicos_asignados["medicina_interna"]
            
            # Asignar el mismo médico a todas las enfermedades
            for enfermedad_nombre in enfermedades:
                enfermedad_id = enfermedad_nombre_a_id.get(enfermedad_nombre)
                if enfermedad_id:
                    nueva_relacion = PacienteEnfermedadMedico(
                        paciente_id=nuevo_paciente.id,
                        enfermedad_id=enfermedad_id,
                        medico_id=medico_medicina_interna_id,
                        estado='ACTIVO'
                    )
                    db.session.add(nueva_relacion)
                    print(f"Asignado médico {medico_medicina_interna_id} (Medicina Interna) para {enfermedad_descripcion[enfermedad_id]}")
        
        else:
            # Caso: Médicos específicos por enfermedad
            for enfermedad_nombre in enfermedades:
                enfermedad_id = enfermedad_nombre_a_id.get(enfermedad_nombre)
                medico_id = medicos_asignados.get(enfermedad_nombre)
                
                if enfermedad_id and medico_id:
                    nueva_relacion = PacienteEnfermedadMedico(
                        paciente_id=nuevo_paciente.id,
                        enfermedad_id=enfermedad_id,
                        medico_id=medico_id,
                        estado='ACTIVO'
                    )
                    db.session.add(nueva_relacion)
                    print(f"Asignado médico {medico_id} para {enfermedad_descripcion[enfermedad_id]}")
        db.session.commit()
        return nuevo_paciente

    @staticmethod
    def obtener_todos_con_filtros_nuevo(estado=None, medico_id=None, fecha_desde=None, fecha_hasta=None, busqueda=None, page=1, per_page=10):
        """
        NUEVO MÉTODO - Obtiene pacientes con filtros 
        """
        query = Paciente.query
        
        # Filtro por estado
        if estado and estado != 'todos':
            query = query.filter(Paciente.estado == estado.upper())
        
        # NUEVO: Filtro por médico usando tabla intermedia
        if medico_id and medico_id != 'todos':
            subquery = db.session.query(PacienteEnfermedadMedico.paciente_id)\
                .filter(PacienteEnfermedadMedico.medico_id == medico_id)\
                .filter(PacienteEnfermedadMedico.estado == 'ACTIVO')\
                .subquery()
            query = query.filter(Paciente.id.in_(subquery))
        
        # Filtro por rango de fechas
        if fecha_desde:
            query = query.filter(Paciente.fecha_registro >= fecha_desde)
        if fecha_hasta:
            query = query.filter(Paciente.fecha_registro <= fecha_hasta)
        
        # Filtro de búsqueda (nombre o DNI)
        if busqueda:
            busqueda_like = f"%{busqueda}%"
            query = query.filter(
                or_(
                    Paciente.nombres.ilike(busqueda_like),
                    Paciente.apellidos.ilike(busqueda_like),
                    Paciente.dni.like(busqueda_like)
                )
            )
        
        # Ordenar por fecha de registro descendente
        query = query.order_by(desc(Paciente.fecha_registro))
        
        # Aplicar paginación
        return query.paginate(page=page, per_page=per_page, error_out=False)
        
    
    
    ########################
    

# ------------------------------------------------------------------------------
# MODELO: Profesional
# Propósito: Representa profesionales médicos y sus especialidades.
# Relaciones:
#   - Relación 1:N con Cita (definida en modelo Cita)
# ------------------------------------------------------------------------------
class Profesional(db.Model):
    __tablename__ = 'profesionales'
    
    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(8), unique=True, nullable=False)  # 
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    especialidad = db.Column(db.Enum('CARDIOLOGÍA', 'MEDICINA INTERNA', 'ENDOCRINOLOGÍA', 'PSICOLOGÍA CLÍNICA', 'NEUMOLOGÍA'), nullable=False)  # ✅ CORREGIDO
    rol = db.Column(db.Enum('MÉDICO', 'PSICÓLOGO'), nullable=False)
    telefono = db.Column(db.String(15))  # 
    email = db.Column(db.String(100), unique=True)  #
    horario_atencion = db.Column(db.JSON)  # 
    pacientes_asignados = db.Column(db.Integer, default=0)  # 
    fecha_registro = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())  # 
    estado = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')  # 
    
    
    ######################### admin-dashboard
    # Propiedades computadas para formato de nombres
    @property
    def primer_nombre(self):
        """Extrae el primer nombre del campo completo (ej: 'Carlos' de 'Carlos Alberto')"""
        return self.nombres.split()[0] if self.nombres else ""

    @property
    def primer_apellido(self):
        """Extrae el primer apellido del campo completo (ej: 'Gomez' de 'Gomez Fernandez')"""
        return self.apellidos.split()[0] if self.apellidos else ""
    
    @property
    def nombre_formal(self):
        """Formato estándar para mostrar: 'PrimerNombre PrimerApellido'"""
        return f"{self.primer_nombre} {self.primer_apellido}".strip()
    
    ######################### 
    
    ######################### admin-pacientes
    @property
    def nombre_completo(self):
        """Retorna nombre completo del profesional"""
        # f"Dr. {self.nombres.split()[0]} {self.apellidos.split()[0]}"
        return f"Dr. {self.nombres} {self.apellidos}"
    
    @staticmethod
    def obtener_medicos_activos():
        """
        Obtiene todos los médicos activos para asignación
        """
        return Profesional.query.filter(
            and_(
                Profesional.rol == 'MÉDICO',
                Profesional.estado == 'ACTIVO'
            )
        ).all() 
    ################
    
      
    
class Cuidador(db.Model):
    __tablename__ = 'cuidadores'
    
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    nombre_completo = db.Column(db.String(200), nullable=False)
    dni = db.Column(db.String(8), nullable=False)
    telefono = db.Column(db.String(15), nullable=False)
    relacion_paciente = db.Column(
        db.Enum('familiar', 'conyugue', 'hijo', 'padre', 'hermano', 'amigo', 'profesional', 'otro'),
        nullable=False
    )
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())
    estado = db.Column(db.Enum('ACTIVO', 'INACTIVO'))
    
    ###########admin-pacientes
    @staticmethod
    def crear_cuidador(paciente_id, nombre_completo, dni, telefono, relacion_paciente):
        """
        Crea un nuevo cuidador para un paciente
        """
        nuevo_cuidador = Cuidador(
            paciente_id=paciente_id,
            nombre_completo=nombre_completo,
            dni=dni,
            telefono=telefono,
            relacion_paciente=relacion_paciente
        )
        
        db.session.add(nuevo_cuidador)
        db.session.commit()
        return nuevo_cuidador
    ###############################
    
    

# models/actores.py - AGREGAR ESTOS MODELOS AL FINAL

class Enfermedad(db.Model):
    __tablename__ = 'enfermedades'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(10), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    especialidad_requerida = db.Column(db.Enum('CARDIOLOGÍA', 'MEDICINA INTERNA', 'ENDOCRINOLOGÍA', 'NEUMOLOGÍA', 'PSICOLOGÍA CLÍNICA'), nullable=False)
    estado = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')
    fecha_creacion = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

class PacienteEnfermedadMedico(db.Model):
    __tablename__ = 'paciente_enfermedad_medico'
    
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    enfermedad_id = db.Column(db.Integer, db.ForeignKey('enfermedades.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('profesionales.id'), nullable=False)
    fecha_asignacion = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    estado = db.Column(db.Enum('ACTIVO', 'INACTIVO'), default='ACTIVO')
    observaciones = db.Column(db.Text)
    
    # Relaciones
    paciente = db.relationship('Paciente', backref='asignaciones_medicas')
    enfermedad = db.relationship('Enfermedad', backref='asignaciones')
    medico = db.relationship('Profesional', backref='pacientes_asignados_enfermedades')