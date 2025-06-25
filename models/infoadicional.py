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

class InfoAdicional:
    def __init__(self, idinfoacicional, desayuno_comida, desayuno_porcion, desayuno_notas, almuerzo_comida, almuerzo_porcion, almuerzo_notas, cena_comida, cena_porcion, cena_notas, actividad, intensidad, tiempo, notas_adicionales, fecha, pacientes_id):
        self.id = idinfoacicional
        self.desayuno_comida = desayuno_comida
        self.desayuno_porcion = desayuno_porcion
        self.desayuno_notas = desayuno_notas
        self.almuerzo_comida = almuerzo_comida
        self.almuerzo_porcion = almuerzo_porcion
        self.almuerzo_notas = almuerzo_notas
        self.cena_comida = cena_comida
        self.cena_porcion = cena_porcion
        self.cena_notas = cena_notas
        self.actividad = actividad
        self.intensidad = intensidad
        self.tiempo = tiempo
        self.notas_adicionales = notas_adicionales
        self.fecha = fecha
        self.pacientes_id = pacientes_id

    @classmethod
    def insertar_dato(cls, desayuno_comida, desayuno_porcion, desayuno_notas, almuerzo_comida, almuerzo_porcion, almuerzo_notas, cena_comida, cena_porcion, cena_notas, actividad, intensidad, tiempo, notas_adicionales, usuarios_id):
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
            INSERT INTO infoadicional (desayuno_comida, desayuno_porcion, desayuno_notas, almuerzo_comida, almuerzo_porcion, almuerzo_notas, cena_comida, cena_porcion, cena_notas, actividad, intensidad, tiempo, notas_adicionales, fecha, pacientes_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)
            """
            cursor.execute(sql_insert, (
                desayuno_comida, 
                desayuno_porcion, 
                desayuno_notas, 
                almuerzo_comida, 
                almuerzo_porcion, 
                almuerzo_notas, 
                cena_comida, 
                cena_porcion, 
                cena_notas, 
                actividad, 
                intensidad, 
                tiempo, 
                notas_adicionales,
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