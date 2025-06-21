# models/cita.py

from . import db
from sqlalchemy import asc, desc
from datetime import datetime, date
from sqlalchemy.exc import SQLAlchemyError
from models.admin_horarios import HorarioDisponible
from models.actores import PacienteEnfermedadMedico, Profesional

class Cita(db.Model):
    __tablename__ = 'citas'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('profesionales.id'), nullable=False)
    horario_id = db.Column(db.Integer, db.ForeignKey('horarios_disponibles.id'), nullable=False)
    enfermedad_id = db.Column(db.Integer, db.ForeignKey('enfermedades.id'), nullable=False)
    
    fecha_cita = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    duracion_minutos = db.Column(db.Integer, nullable=False, default=60)
    tipo = db.Column(db.Enum('PRESENCIAL', 'VIRTUAL'), nullable=False)
    consultorio = db.Column(db.String(50))
    
    especialidad = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.Enum('AGENDADA', 'ATENDIDA', 'NO_ATENDIDA', 'CANCELADA'), default='AGENDADA')
    
    motivo_consulta = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    enlace_virtual = db.Column(db.String(255))
    
    fecha_creacion = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    fecha_actualizacion = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    paciente = db.relationship('Paciente', backref='citas', lazy='select')
    medico = db.relationship('Profesional', backref='citas_asignadas', lazy='select')
    horario = db.relationship('HorarioDisponible', backref='citas_programadas', lazy='select')
    enfermedad = db.relationship('Enfermedad', backref='citas_relacionadas', lazy='select')
    
    
    
    def informacion_cita(self):
        return {
            'id': self.id,
            'paciente_id': self.paciente_id,
            'medico_id': self.medico_id,
            'horario_id': self.horario_id,
            'enfermedad_id': self.enfermedad_id,
            'fecha_cita': self.fecha_cita.isoformat() if self.fecha_cita else None,
            'hora_inicio': self.hora_inicio.strftime('%H:%M') if self.hora_inicio else None,
            'hora_fin': self.hora_fin.strftime('%H:%M') if self.hora_fin else None,
            'duracion_minutos': self.duracion_minutos,
            'tipo': self.tipo,
            'consultorio': self.consultorio,
            'especialidad': self.especialidad,
            'estado': self.estado,
            'motivo_consulta': self.motivo_consulta,
            'observaciones': self.observaciones,
            'enlace_virtual': self.enlace_virtual
        }
    
    def __repr__(self):
        return f'<Cita {self.id}: Paciente {self.paciente_id} - {self.fecha_cita}>'
    
    @staticmethod
    def crear_cita(datos_cita):
        """Crea una nueva cita y actualiza el horario disponible."""
        
        # Validaciones básicas
        if not datos_cita.get('paciente_id'):
            return {'success': False, 'error': 'paciente_id requerido'}
        
        if not datos_cita.get('horario_id'):
            return {'success': False, 'error': 'horario_id requerido'}
            
        if not datos_cita.get('enfermedad_id'):
            return {'success': False, 'error': 'enfermedad_id requerido'}
        
        try:
            db.session.begin()
            
            # Obtener y bloquear el horario
            horario = HorarioDisponible.query.with_for_update().filter_by(
                id=datos_cita['horario_id'], 
                estado='ACTIVO'
            ).first()
            
            if not horario:
                db.session.rollback()
                return {'success': False, 'error': 'Horario no disponible'}
            
            # Verificar asignación médico-paciente-enfermedad
            asignacion = PacienteEnfermedadMedico.query.filter_by(
                paciente_id=datos_cita['paciente_id'],
                enfermedad_id=datos_cita['enfermedad_id'],
                estado='ACTIVO'
            ).first()
            
            if not asignacion:
                db.session.rollback()
                return {'success': False, 'error': 'No hay médico asignado'}
            
            # Obtener especialidad del médico
            profesional = Profesional.query.get(asignacion.medico_id)
            if not profesional:
                db.session.rollback()
                return {'success': False, 'error': 'Médico no encontrado'}
            
            # Crear enlace virtual si es necesario
            enlace_virtual = None
            if datos_cita.get('tipo', 'PRESENCIAL') == 'VIRTUAL':
                enlace_virtual = f"https://meet.clinic.com/cita-{datos_cita['horario_id']}"
            
            # Crear la cita
            nueva_cita = Cita(
                paciente_id=datos_cita['paciente_id'],
                medico_id=asignacion.medico_id,
                horario_id=datos_cita['horario_id'],
                enfermedad_id=datos_cita['enfermedad_id'],
                fecha_cita=horario.fecha,
                hora_inicio=horario.hora_inicio,
                hora_fin=horario.hora_fin,
                duracion_minutos=datos_cita.get('duracion_minutos', 60),
                tipo=datos_cita.get('tipo', 'PRESENCIAL'),
                consultorio=horario.consultorio,
                especialidad=profesional.especialidad,
                motivo_consulta=datos_cita.get('motivo_consulta', ''),
                enlace_virtual=enlace_virtual,
                estado='AGENDADA'
            )
            
            # Actualizar el horario a INACTIVO
            horario.estado = 'INACTIVO'
            
            # Guardar cambios
            db.session.add(nueva_cita)
            db.session.commit()
            
            return {
                'success': True,
                'cita_id': nueva_cita.id,
                'message': f'Cita agendada para el {horario.fecha}'
            }
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error de BD: {str(e)}'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error: {str(e)}'}
    
    @staticmethod
    def cancelar_cita(cita_id):
        """Cancela una cita y libera el horario."""
        try:
            db.session.begin()
            
            cita = Cita.query.with_for_update().get(cita_id)
            if not cita:
                db.session.rollback()
                return {'success': False, 'error': 'Cita no encontrada'}
            
            if cita.estado == 'CANCELADA':
                db.session.rollback()
                return {'success': False, 'error': 'Cita ya cancelada'}
            
            # Liberar el horario
            horario = HorarioDisponible.query.with_for_update().get(cita.horario_id)
            if horario:
                horario.estado = 'ACTIVO'
            
            # Cancelar la cita
            cita.estado = 'CANCELADA'
            
            db.session.commit()
            return {'success': True, 'message': 'Cita cancelada'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error: {str(e)}'}
    
    @staticmethod
    def obtener_cita(cita_id):
        """Obtiene una cita por ID."""
        try:
            cita = Cita.query.get(cita_id)
            if not cita:
                return {'success': False, 'error': 'Cita no encontrada'}
            
            return {'success': True, 'cita': cita}
        except Exception as e:
            return {'success': False, 'error': f'Error: {str(e)}'}
    
    @staticmethod
    def obtener_citas_hoy():
        """
        Obtiene citas agendadas para el día actual.
        
        Returns:
            list: Citas ordenadas por hora de inicio ascendente
            
        Notas:
            - Filtra por fecha actual del sistema (date.today())
            - Ordena de la cita más temprana a la más tardía
        """
        hoy = date.today()
        return Cita.query.filter(Cita.fecha_cita == hoy).order_by(asc(Cita.hora_inicio)).all()
    
    @staticmethod
    def obtener_citas_por_horario(horario_id):
        """
        Obtiene todas las citas asociadas a un horario específico.
        
        Args:
            horario_id (int): ID del horario
            
        Returns:
            list: Lista de citas del horario
        """
        return Cita.query.filter_by(horario_id=horario_id).all()
    
    @staticmethod
    def obtener_citas_activas_por_horario(horario_id):
        """
        Obtiene solo las citas agendadas (no canceladas) de un horario.
        
        Args:
            horario_id (int): ID del horario
            
        Returns:
            list: Lista de citas activas del horario
        """
        return Cita.query.filter(
            Cita.horario_id == horario_id,
            Cita.estado == 'AGENDADA'
        ).all()
    
    @property
    def duracion_formateada(self):
        """
        Retorna la duración de la cita en formato legible.
        """
        if self.duracion_minutos >= 60:
            horas = self.duracion_minutos // 60
            minutos = self.duracion_minutos % 60
            if minutos > 0:
                return f"{horas}h {minutos}min"
            return f"{horas}h"
        return f"{self.duracion_minutos}min"
    
    @property
    def horario_completo(self):
        """
        Retorna el horario completo de la cita en formato legible.
        """
        return f"{self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')}"