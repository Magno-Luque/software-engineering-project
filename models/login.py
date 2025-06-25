# models/login.py

import bcrypt

class Usuario:
    """Modelo para la tabla usuarios usando Flask-MySQLdb"""
    
    def __init__(self, mysql):
        self.mysql = mysql
    
    @classmethod
    def validar_credenciales(cls, mysql, correo, password):
        """Valida las credenciales del usuario usando el correo"""
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT id, usuario, password, rol, correo, activo, fecha_creacion 
                FROM usuarios 
                WHERE correo = %s AND activo = 1
            """
            cursor.execute(query, (correo.strip(),))
            row = cursor.fetchone()
            cursor.close()
            
            if not row:
                print(f"Usuario no encontrado con correo: {correo}")
                return None
            
            # Convertir manualmente a diccionario
            usuario_data = {
                'id': row['id'],
                'usuario': row['usuario'],
                'password': row['password'],
                'rol': row['rol'],
                'correo': row['correo'],
                'activo': row['activo'],
                'fecha_creacion': row['fecha_creacion'],
            }

            # Verificar contraseña
            stored_password = usuario_data['password']      
            
            if stored_password.startswith('$2b$'):
                # Comparación directa para modo desarrollo
                if bcrypt.checkpw( password.encode('utf-8'), usuario_data['password'].encode('utf-8')):
                    print(f"Login exitoso para correo: {correo}")
                    return usuario_data
                else:
                    print(f"Contraseña incorrecta para correo: {correo}")
                    return None

        except Exception as e:
            print(f"Error al validar credenciales para correo {correo}: {str(e)}")
            return None

    
    @classmethod
    def obtener_por_id(cls, mysql, user_id):
        """Obtiene un usuario por su ID"""
        try:
            cursor = mysql.connection.cursor()
            query = """
                SELECT id, usuario, rol, correo, activo, fecha_creacion 
                FROM usuarios 
                WHERE id = %s
            """
            cursor.execute(query, (user_id,))
            usuario_data = cursor.fetchone()
            cursor.close()
            return usuario_data
        except Exception as e:
            print(f"Error al obtener usuario por ID {user_id}: {str(e)}")
            return None
    
    @classmethod
    def crear_usuario(cls, mysql, usuario_data):
        """Crea un nuevo usuario"""
        try:
            cursor = mysql.connection.cursor()
            
            # Hash de la contraseña
            password_hash = bcrypt.hashpw(
                usuario_data['password'].encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            query = """
                INSERT INTO usuarios (usuario, password, rol, correo, activo) 
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                usuario_data['usuario'],
                password_hash,
                usuario_data['rol'],
                usuario_data['correo'],
                usuario_data.get('activo', True)
            ))
            
            mysql.connection.commit()
            user_id = cursor.lastrowid
            cursor.close()
            
            print(f"Usuario creado exitosamente con ID: {user_id}")
            return user_id
            
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al crear usuario: {str(e)}")
            return None
    
    @classmethod
    def obtener_todos(cls, mysql):
        """Obtiene todos los usuarios activos"""
        try:
            cursor = mysql.connection.cursor()
            query = """
                SELECT id, usuario, rol, correo, activo, fecha_creacion 
                FROM usuarios 
                WHERE activo = 1
                ORDER BY fecha_creacion DESC
            """
            cursor.execute(query)
            usuarios = cursor.fetchall()
            cursor.close()
            return usuarios
        except Exception as e:
            print(f"Error al obtener usuarios: {str(e)}")
            return []
    
    @staticmethod
    def to_dict(usuario_data):
        """Convierte los datos del usuario a diccionario (sin password)"""
        if not usuario_data:
            return None
            
        return {
            'id': usuario_data['id'],
            'usuario': usuario_data['usuario'],
            'rol': usuario_data['rol'],
            'correo': usuario_data['correo'],
            'activo': usuario_data['activo'],
            'fecha_creacion': usuario_data['fecha_creacion'].isoformat() if usuario_data.get('fecha_creacion') else None
        }