# models/__init__.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importar todos los modelos para que estén disponibles
from .actores import Paciente, Profesional, Cuidador, Enfermedad, PacienteEnfermedadMedico

from .admin_dashboard import ResumenDashboard, Cita
from .admin_horarios import HorarioDisponible, PlantillaHorario

