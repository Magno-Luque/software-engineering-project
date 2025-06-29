# config/config.py

import mysql.connector
from mysql.connector import Error
import os

# Configuración Flask y Base de Datos
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu-clave-secreta-compleja'
    
    # Configuración MySQL
    MYSQL_HOST = 'maglev.proxy.rlwy.net'
    MYSQL_PORT = 55747
    MYSQL_USER = 'magno'
    MYSQL_PASSWORD = 'qw1234'
    MYSQL_DB = 'db_final'
    MYSQL_CURSORCLASS = 'DictCursor'

# Función de conexión usando la configuración
def connectionBD():
    try:
        conexion = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            database=Config.MYSQL_DB,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            charset='utf8mb4',
            port=Config.MYSQL_PORT
        )
        if conexion.is_connected():
            print("Conexión exitosa a la base de datos.")
            return conexion
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def test_connection():
    """Prueba la conexión a la base de datos"""
    conn = connectionBD()
    if conn:
        print("🟢 Conexión exitosa")
        conn.close()
        return True
    else:
        print("🔴 Error de conexión")
        return False
