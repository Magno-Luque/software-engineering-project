# config/config.py

from datetime import timedelta

class Config:
    """
    Configuración principal de la aplicación Flask
    """
    
    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://app_db:12344321@yamabiko.proxy.rlwy.net:48389/db_proof'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Clave secreta para sesiones
    SECRET_KEY = 'clave_secreta_segura'
    
