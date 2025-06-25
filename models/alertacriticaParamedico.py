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
    def obtener_alertas_para_paramedico(cls):
        """Obtiene todas las alertas críticas con información del paciente para paramédicos"""
        conexion_MySQLdb = connectionBD()
        if conexion_MySQLdb is None:
            print("Error: No se pudo conectar a la base de datos.")
            return None

        cursor = conexion_MySQLdb.cursor(dictionary=True)
        
        try:
            sql = """
            SELECT 
                a.id,
                a.pacientes_id,
                a.glucosa,
                a.sistolica,
                a.diastolica,
                a.frecuencia_cardiaca,
                a.fecha,
                a.estado,
                a.nota,
                a.informacion,
                a.paramedicos_id,
                p.dni,
                CONCAT(p.nombres, ' ', p.apellidos) AS nombre_completo,
                p.enfermedad
            FROM alertascriticas a
            JOIN pacientes p ON a.pacientes_id = p.id
            ORDER BY a.fecha DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
            
        except pymysql.Error as e:
            print(f"Error en base de datos: {e}")
            return None
        finally:
            cursor.close()
            conexion_MySQLdb.close()

    @classmethod
    def actualizar_estado_alerta(cls, alerta_id, nuevo_estado, paramedico_id, nota=None):
        """Actualiza el estado de una alerta validando el paramédico"""
        conexion_MySQLdb = connectionBD()
        if conexion_MySQLdb is None:
            print("Error: No se pudo conectar a la base de datos.")
            return False

        cursor = conexion_MySQLdb.cursor()
        
        try:
            # Primero verificar que el paramédico existe
            cursor.execute("SELECT id FROM paramedicos WHERE id = %s", (paramedico_id,))
            if not cursor.fetchone():
                print(f"Error: Paramédico con ID {paramedico_id} no existe")
                return False

            if nota:
                sql = """
                UPDATE alertascriticas 
                SET estado = %s, nota = %s, paramedicos_id = %s 
                WHERE id = %s
                """
                cursor.execute(sql, (nuevo_estado, nota, paramedico_id, alerta_id))
            else:
                sql = """
                UPDATE alertascriticas 
                SET estado = %s, paramedicos_id = %s 
                WHERE id = %s
                """
                cursor.execute(sql, (nuevo_estado, paramedico_id, alerta_id))
            
            conexion_MySQLdb.commit()
            return cursor.rowcount > 0
            
        except pymysql.Error as e:
            print(f"Error en base de datos: {e}")
            conexion_MySQLdb.rollback()
            return False
        finally:
            cursor.close()
            conexion_MySQLdb.close()