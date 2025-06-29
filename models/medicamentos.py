import pymysql
from datetime import datetime
from config.config import connectionBD
from flask import session

class Usuario:
    def __init__(self, id, usuario, password, rol, activo, fecha_creacion, correo):
        self.id = id
        self.usuario = usuario
        self.password = password
        self.rol = rol
        self.activo = activo
        self.fecha_creacion = fecha_creacion
        self.correo = correo

class Paciente:
    def __init__(self, id, dni, nombres, apellidos, telefono, edad, fecha_nacimiento, direccion, activo, enfermedad, usuarios_id1):
        self.id = id
        self.dni = dni
        self.nombres = nombres
        self.apellidos = apellidos
        self.telefono = telefono
        self.edad = edad
        self.fecha_nacimiento = fecha_nacimiento
        self.direccion = direccion
        self.activo = activo
        self.enfermedad = enfermedad
        self.usuarios_id1 = usuarios_id1

class Medicamentos:
    def __init__(self, idmedicamentos, medicamentos, dosis, frecuencia, duracion, horario_dia, horario_tarde, horario_noche, indicaciones, fecha, pacientes_id):
        self.id = idmedicamentos
        self.medicamentos = medicamentos
        self.dosis = dosis
        self.frecuencia = frecuencia
        self.duracion = duracion
        self.horario_dia = horario_dia
        self.horario_tarde = horario_tarde
        self.horario_noche = horario_noche
        self.indicaciones = indicaciones
        self.fecha = fecha
        self.pacientes_id = pacientes_id

    @classmethod
    def obtener_medicamentos_por_usuario(cls, usuario_id):
        """Obtiene los medicamentos del paciente asociado a un usuario."""
        conexion_MySQLdb = connectionBD()
        if conexion_MySQLdb is None:
            print("Error: No se pudo conectar a la base de datos.")
            return None

        cursor = conexion_MySQLdb.cursor(dictionary=True)
        
        try:
            sql_paciente = "SELECT id FROM pacientes WHERE usuarios_id1 = %s"
            cursor.execute(sql_paciente, (usuario_id,))
            paciente = cursor.fetchone()
            
            if not paciente:
                print("No existe paciente asociado a este usuario")
                return None

            sql_medicamentos = """
            SELECT 
                idmedicamentos,
                medicamento,
                dosis,
                frecuencia,
                duracion,
                TIME_FORMAT(horario_dia, '%H:%i') as horario_dia,
                TIME_FORMAT(horario_tarde, '%H:%i') as horario_tarde,
                TIME_FORMAT(horario_noche, '%H:%i') as horario_noche,
                indicaciones,
                fecha,
                pacientes_id
            FROM medicamentos
            WHERE pacientes_id = %s
            ORDER BY fecha DESC
            """
            cursor.execute(sql_medicamentos, (paciente['id'],))
            return cursor.fetchall()
            
        except pymysql.Error as e:
            print(f"Error en base de datos: {e}")
            return None
        finally:
            cursor.close()
            conexion_MySQLdb.close()