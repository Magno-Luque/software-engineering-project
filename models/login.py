# models/login.py

import bcrypt
from datetime import datetime
from . import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum('admin','medico','psicologo','paciente','cuidador','paramedico'), nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=True)
    fecha_creacion = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=True)
    correo = db.Column(db.String(50), nullable=False)
    
    @classmethod
    def validar_credenciales(cls, correo, password):
        """Valida las credenciales del usuario usando el correo"""
        try:
            # Buscar usuario activo por correo
            usuario = cls.query.filter_by(
                correo=correo.strip(), 
                activo=True
            ).first()
            
            if not usuario:
                print(f"Usuario no encontrado con correo: {correo}")
                return None
            
            # Verificar contraseña
            password_bytes = password.encode('utf-8')
            stored_password = usuario.password
            
            # Si la contraseña almacenada no empieza con $2b$, podría ser texto plano (desarrollo)
            if not stored_password.startswith('$2b$'):
                # Para desarrollo/testing - comparación directa (NO usar en producción)
                if stored_password == password:
                    print(f"Login exitoso (modo desarrollo) para correo: {correo}")
                    return usuario
                else:
                    print(f"Contraseña incorrecta (modo desarrollo) para correo: {correo}")
                    return None
            
            # Verificación con bcrypt
            if bcrypt.checkpw(password_bytes, stored_password.encode('utf-8')):
                print(f"Login exitoso para correo: {correo}")
                return usuario
            else:
                print(f"Contraseña incorrecta para correo: {correo}")
                return None
                
        except Exception as e:
            print(f"Error al validar credenciales para correo {correo}: {str(e)}")
            return None
    
    def to_dict(self):
        """Convierte el usuario a diccionario (sin password)"""
        return {
            'id': self.id,
            'usuario': self.usuario,
            'rol': self.rol,
            'correo': self.correo,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
    
    def __repr__(self):
        return f'<Usuario {self.usuario} - {self.rol}>'