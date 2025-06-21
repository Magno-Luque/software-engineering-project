# models/admin_dashboard.py

from . import db
from sqlalchemy import asc, desc
from datetime import date
from models.cita import Cita


# ------------------------------------------------------------------------------
# MODELO: ResumenDashboard
# Propósito: Almacena métricas precalculadas para el panel de administración.
# Notas:
#   - Diseñado como tabla singleton (solo 1 registro) para acceso rápido
#   - Los valores se actualizan mediante procesos batch, no en tiempo real
# ------------------------------------------------------------------------------
class ResumenDashboard(db.Model):
    __tablename__ = 'resumen_dashboard'
    
    id = db.Column(db.Integer, primary_key=True)
    total_pacientes = db.Column(db.Integer, default=0)
    total_profesionales = db.Column(db.Integer, default=0)
    citas_hoy = db.Column(db.Integer, default=0)
    alertas_criticas_activas = db.Column(db.Integer, default=0)
    fecha_actualizacion = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    @staticmethod
    def obtener_resumen():
        """
        Retorna el resumen de métricas del dashboard.
        
        Returns:
            dict/None: Diccionario con métricas o None si no existe registro.
            
        Notas:
            - Solo debe existir un registro en esta tabla
            - Los valores se actualizan periódicamente, no en cada operación
        """
        resumen = ResumenDashboard.query.first()
        if resumen:
            return {
                'total_pacientes': resumen.total_pacientes,
                'total_profesionales': resumen.total_profesionales,
                'total_citas_hoy': resumen.citas_hoy,
                'total_alertas_criticas': resumen.alertas_criticas_activas
            }
        return {
            'total_pacientes': 0,
            'total_profesionales': 0,
            'total_citas_hoy': 0,
            'total_alertas_criticas': 0
        }

# # ------------------------------------------------------------------------------
# # MODELO: Cita - ACTUALIZADO PARA NUEVA ESTRUCTURA
# # Propósito: Gestiona las citas médicas entre pacientes y profesionales.
# # Comportamiento:
# #   - Estado por defecto: 'AGENDADA'
# #   - Las relaciones usan backref para acceso bidireccional
# # ------------------------------------------------------------------------------
# class Cita(db.Model):
#     __tablename__ = 'citas'
    
#     id = db.Column(db.Integer, primary_key=True)
#     paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
#     medico_id = db.Column(db.Integer, db.ForeignKey('profesionales.id'), nullable=False)
#     horario_id = db.Column(db.Integer, db.ForeignKey('horarios_disponibles.id'), nullable=False)  # OBLIGATORIO
#     enfermedad_id = db.Column(db.Integer, db.ForeignKey('enfermedades.id'), nullable=False)  # OBLIGATORIO
    
#     # Información de la cita (copiada del horario)
#     fecha_cita = db.Column(db.Date, nullable=False)
#     hora_inicio = db.Column(db.Time, nullable=False)  # Cambió de hora_cita
#     hora_fin = db.Column(db.Time, nullable=False)     # NUEVO
#     duracion_minutos = db.Column(db.Integer, nullable=False, default=60)  # NUEVO
#     tipo = db.Column(db.Enum('PRESENCIAL', 'VIRTUAL'), nullable=False)
#     consultorio = db.Column(db.String(50))  # NUEVO: para citas presenciales
    
#     # Información del médico (para evitar JOINs repetitivos)
#     especialidad = db.Column(db.String(50), nullable=False)
    
#     # Estado simplificado
#     estado = db.Column(db.Enum('AGENDADA', 'ATENDIDA', 'NO_ATENDIDA', 'CANCELADA'), default='AGENDADA')
    
#     # Información adicional
#     motivo_consulta = db.Column(db.Text)  # NUEVO: motivo de la consulta
#     observaciones = db.Column(db.Text)    # Observaciones generales
#     enlace_virtual = db.Column(db.String(255))  # Para citas virtuales
    
#     # Auditoría
#     fecha_creacion = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
#     fecha_actualizacion = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
#     # Relaciones - usando lazy loading para evitar problemas circulares
#     paciente = db.relationship('Paciente', backref='citas', lazy='select')
#     medico = db.relationship('Profesional', backref='citas_asignadas', lazy='select')
#     horario = db.relationship('HorarioDisponible', backref='citas_programadas', lazy='select')
#     enfermedad = db.relationship('Enfermedad', backref='citas_relacionadas', lazy='select')
    
#     @staticmethod
#     def obtener_citas_hoy():
#         """
#         Obtiene citas agendadas para el día actual.
        
#         Returns:
#             list: Citas ordenadas por hora de inicio ascendente
            
#         Notas:
#             - Filtra por fecha actual del sistema (date.today())
#             - Ordena de la cita más temprana a la más tardía
#         """
#         hoy = date.today()
#         return Cita.query.filter(Cita.fecha_cita == hoy).order_by(asc(Cita.hora_inicio)).all()
    
#     @staticmethod
#     def obtener_citas_por_horario(horario_id):
#         """
#         Obtiene todas las citas asociadas a un horario específico.
        
#         Args:
#             horario_id (int): ID del horario
            
#         Returns:
#             list: Lista de citas del horario
#         """
#         return Cita.query.filter_by(horario_id=horario_id).all()
    
#     @staticmethod
#     def obtener_citas_activas_por_horario(horario_id):
#         """
#         Obtiene solo las citas agendadas (no canceladas) de un horario.
        
#         Args:
#             horario_id (int): ID del horario
            
#         Returns:
#             list: Lista de citas activas del horario
#         """
#         return Cita.query.filter(
#             Cita.horario_id == horario_id,
#             Cita.estado == 'AGENDADA'
#         ).all()
    
#     @property
#     def duracion_formateada(self):
#         """
#         Retorna la duración de la cita en formato legible.
#         """
#         if self.duracion_minutos >= 60:
#             horas = self.duracion_minutos // 60
#             minutos = self.duracion_minutos % 60
#             if minutos > 0:
#                 return f"{horas}h {minutos}min"
#             return f"{horas}h"
#         return f"{self.duracion_minutos}min"
    
#     @property
#     def horario_completo(self):
#         """
#         Retorna el horario completo de la cita en formato legible.
#         """
#         return f"{self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')}"