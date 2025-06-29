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
    def __init__(self, id, dni, nombres, apellidos, fecha_nacimiento, telefono, email, direccion, enfermedades, fecha_registro, estado, usuarios_id1):
        self.id = id
        self.dni = dni
        self.nombres = nombres
        self.apellidos = apellidos
        self.fecha_nacimiento = fecha_nacimiento
        self.telefono = telefono
        self.email = email
        self.direccion = direccion
        self.enfermedades = enfermedades
        self.fecha_registro = fecha_registro
        self.estado = estado
        self.usuarios_id1 = usuarios_id1

class Alerta:
    def __init__(self, id, pacientes_id, glucosa, sistolica, diastolica, frecuencia_cardiaca, fecha, estado, nota, informacion, paramedicos_id):
        self.id = id
        self.pacientes_id = pacientes_id
        self.glucosa = glucosa
        self.sistolica = sistolica
        self.diastolica = diastolica
        self.frecuencia_cardiaca = frecuencia_cardiaca
        self.fecha = fecha
        self.estado = estado
        self.nota = nota
        self.informacion = informacion
        self.paramedicos_id = paramedicos_id

    @classmethod
    def obtener_alerta_por_usuario(cls, usuario_id):
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

            sql_alerta = """
            SELECT 
                id,
                glucosa,
                sistolica,
                diastolica,
                frecuencia_cardiaca,
                fecha,
                estado,
                nota,
                informacion
            FROM alertascriticas
            WHERE pacientes_id = %s
            ORDER BY fecha DESC
            """
            cursor.execute(sql_alerta, (paciente['id'],))
            return cursor.fetchall()
            
        except pymysql.Error as e:
            print(f"Error en base de datos: {e}")
            return None
        finally:
            cursor.close()
            conexion_MySQLdb.close()