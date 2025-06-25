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

class Dato:
    def __init__(self, iddatos, glucosa, sistolica, diastolica, frecuencia_cardiaca, fecha, descripcion, pacientes_id):
        self.iddatos = iddatos
        self.glucosa = glucosa
        self.sistolica = sistolica
        self.diastolica = diastolica
        self.frecuencia_cardiaca = frecuencia_cardiaca
        self.fecha = fecha
        self.descripcion = descripcion
        self.pacientes_id = pacientes_id

    @classmethod
    def insertar_dato(cls, glucosa, sistolica, diastolica, frecuencia_cardiaca, descripcion, usuarios_id):
        conexion_MySQLdb = connectionBD()
        if conexion_MySQLdb is None:
            print("Error: No se pudo conectar a la base de datos.")
            return None

        cursor = conexion_MySQLdb.cursor(dictionary=True)
        
        try:
            sql_paciente = "SELECT id FROM pacientes WHERE usuarios_id1 = %s"
            cursor.execute(sql_paciente, (session['user_id'],))
            paciente = cursor.fetchone()
            
            if not paciente:
                print("No existe paciente asociado a este usuario")
                return False

            sql_insert = """
            INSERT INTO datos (glucosa, sistolica, diastolica, frecuencia_cardiaca, fecha, descripcion, pacientes_id)
            VALUES (%s, %s, %s, %s, NOW(), %s, %s)
            """
            cursor.execute(sql_insert, (
                glucosa, 
                sistolica, 
                diastolica, 
                frecuencia_cardiaca, 
                descripcion, 
                paciente['id']
            ))
            
            conexion_MySQLdb.commit()
            return True
            
        except pymysql.Error as e:
            print(f"Error en base de datos: {e}")
            conexion_MySQLdb.rollback()
            return False
        finally:
            cursor.close()
            conexion_MySQLdb.close()