# models/admin_horarios.py

from . import db
from sqlalchemy import asc, desc, and_, or_
from datetime import datetime, date, time, timedelta  

# ------------------------------------------------------------------------------
# MODELO: HorarioDisponible - MÉTODO CORREGIDO
# ------------------------------------------------------------------------------
class HorarioDisponible(db.Model):
    __tablename__ = 'horarios_disponibles'
    
    id = db.Column(db.Integer, primary_key=True)
    medico_id = db.Column(db.Integer, db.ForeignKey('profesionales.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    tipo = db.Column(db.Enum('PRESENCIAL', 'VIRTUAL', 'MIXTO'), default='PRESENCIAL')
    consultorio = db.Column(db.String(50))
    duracion_cita = db.Column(db.Integer, default=60)  # minutos
    estado = db.Column(db.Enum('ACTIVO', 'INACTIVO', 'BLOQUEADO'), default='ACTIVO')
    observaciones = db.Column(db.Text)
    fecha_creacion = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    fecha_actualizacion = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Relaciones
    medico = db.relationship('Profesional', backref='horarios_disponibles', lazy=True)
    citas = db.relationship('Cita', backref='horario_original', lazy=True)
    
    @staticmethod
    def obtener_horarios_semana(fecha_inicio, fecha_fin):
        """
        Obtiene horarios activos de una semana específica.
        """
        return HorarioDisponible.query.filter(
            and_(
                HorarioDisponible.fecha >= fecha_inicio,
                HorarioDisponible.fecha <= fecha_fin,
                # HorarioDisponible.estado == 'ACTIVO'
            )
        ).join(HorarioDisponible.medico).order_by(
            HorarioDisponible.fecha,
            HorarioDisponible.hora_inicio
        ).all()
    
    @staticmethod
    def verificar_conflicto_horario(medico_id, fecha, hora_inicio, hora_fin, excluir_id=None):
        """
        Verifica si existe conflicto de horarios para un médico.
        """
        query = HorarioDisponible.query.filter(
            and_(
                HorarioDisponible.medico_id == medico_id,
                HorarioDisponible.fecha == fecha,
                # HorarioDisponible.estado == 'ACTIVO',
                or_(
                    and_(HorarioDisponible.hora_inicio <= hora_inicio, HorarioDisponible.hora_fin > hora_inicio),
                    and_(HorarioDisponible.hora_inicio < hora_fin, HorarioDisponible.hora_fin >= hora_fin),
                    and_(HorarioDisponible.hora_inicio >= hora_inicio, HorarioDisponible.hora_fin <= hora_fin)
                )
            )
        ) 
        
        if excluir_id:
            query = query.filter(HorarioDisponible.id != excluir_id)
        
        return query.first()
    
    @staticmethod
    def crear_horario(datos_horario):
        """
        Crea un nuevo horario disponible en la base de datos.
        """
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
        
        nuevo_horario = HorarioDisponible(
            medico_id=datos_horario['medico_id'],
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            tipo=datos_horario.get('tipo', 'PRESENCIAL'),
            consultorio=datos_horario.get('consultorio'),
            observaciones=datos_horario.get('observaciones'),
            duracion_cita=datos_horario.get('duracion_cita', 60)
        )
        
        db.session.add(nuevo_horario)
        db.session.commit()
        return nuevo_horario
    
    @staticmethod
    def obtener_por_id(horario_id):
        """
        Obtiene un horario específico por su ID.
        """
        return HorarioDisponible.query.filter_by(id=horario_id).join(HorarioDisponible.medico).first()
    
    @staticmethod
    def eliminar_horario(horario_id):
        """
        Elimina un horario disponible de la base de datos.
        """
        horario = HorarioDisponible.query.get(horario_id)
        if not horario:
            return False
        
        # Verificar citas agendadas
        from .admin_dashboard import Cita  # Import aquí para evitar circular
        citas_activas = Cita.query.filter(
            and_(
                Cita.horario_id == horario_id,
                Cita.estado == 'AGENDADA'
            )
        ).count()
        
        if citas_activas > 0:
            raise ValueError(f'No se puede eliminar: tiene {citas_activas} cita(s) agendada(s)')
        
        db.session.delete(horario)
        db.session.commit()
        return True
    
    @property
    def esta_ocupado(self):
        """
        Verifica si el horario tiene citas agendadas.
        """
        #return len([cita for cita in self.citas if cita.estado == 'AGENDADA']) > 0
        #print(self.estado)
        return True if self.estado == "INACTIVO" else False
    
    @property
    def nombre_medico_completo(self):
        """
        Retorna el nombre completo formateado del médico.
        """
        if hasattr(self.medico, 'nombre_formal'):
            return self.medico.nombre_formal
        return f"Dr. {self.medico.nombres} {self.medico.apellidos}"
    
    # Agregar este método estático en la clase HorarioDisponible en models/admin_horarios.py

    @staticmethod
    def actualizar_horario(horario_id, datos_horario):
        """
        Actualiza un horario disponible existente en la base de datos.
        """
        horario = HorarioDisponible.query.get(horario_id)
        if not horario:
            raise ValueError('Horario no encontrado')
        
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
        
        # Actualizar campos
        horario.medico_id = datos_horario['medico_id']
        horario.fecha = fecha
        horario.hora_inicio = hora_inicio
        horario.hora_fin = hora_fin
        horario.tipo = datos_horario.get('tipo', 'PRESENCIAL')
        horario.consultorio = datos_horario.get('consultorio')
        horario.observaciones = datos_horario.get('observaciones')
        horario.duracion_cita = datos_horario.get('duracion_cita', 60)
        
        # Actualizar timestamp
        horario.fecha_actualizacion = db.func.current_timestamp()
        
        db.session.commit()
        return horario

    @staticmethod
    def crear_horarios_rango(datos_horario):
        """
        NUEVA FUNCIÓN: Crea múltiples slots de 1 hora a partir de un rango.
        """
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
            conflicto = HorarioDisponible.verificar_conflicto_horario(
                datos_horario['medico_id'], 
                fecha, 
                hora_actual.time(), 
                hora_siguiente.time()
            )
            
            if conflicto:
                raise ValueError(f'Conflicto en slot {hora_actual.time().strftime("%H:%M")}-{hora_siguiente.time().strftime("%H:%M")}: ya existe un horario')
            
            # Crear el slot usando tu función existente
            slot_datos = datos_horario.copy()
            slot_datos['hora_inicio'] = hora_actual.time()
            slot_datos['hora_fin'] = hora_siguiente.time()
            
            nuevo_slot = HorarioDisponible.crear_horario(slot_datos)
            slots_creados.append(nuevo_slot)
            
            hora_actual = hora_siguiente
        
        return slots_creados

# ------------------------------------------------------------------------------
# MODELO: PlantillaHorario
# ------------------------------------------------------------------------------
class PlantillaHorario(db.Model):
    __tablename__ = 'plantillas_horarios'
    
    id = db.Column(db.Integer, primary_key=True)
    medico_id = db.Column(db.Integer, db.ForeignKey('profesionales.id'), nullable=False)
    dia_semana = db.Column(db.Enum('LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO'), nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    tipo = db.Column(db.Enum('PRESENCIAL', 'VIRTUAL', 'MIXTO'), default='PRESENCIAL')
    consultorio = db.Column(db.String(50))
    duracion_cita = db.Column(db.Integer, default=60)
    activo = db.Column(db.Boolean, default=True)
    fecha_inicio = db.Column(db.Date)  # Desde cuándo aplica
    fecha_fin = db.Column(db.Date)     # Hasta cuándo aplica (NULL = indefinido)
    
    # Relación
    medico = db.relationship('Profesional', backref='plantillas_horarios', lazy=True)
    
    @staticmethod
    def obtener_plantillas_activas_por_medico(medico_id):
        """
        Obtiene plantillas activas de un médico específico.
        """
        return PlantillaHorario.query.filter(
            and_(
                PlantillaHorario.medico_id == medico_id,
                PlantillaHorario.activo == True
            )
        ).order_by(PlantillaHorario.dia_semana).all()