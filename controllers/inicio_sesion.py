from flask import render_template, redirect, url_for, flash, request, session, jsonify
from models.login import Usuario

class AuthController:
    @staticmethod
    def procesar_login():
        """Procesa el formulario de login (web tradicional)"""
        # Importar mysql desde app
        from app import mysql
        
        # Si ya está autenticado, redirigir
        if 'user_id' in session and 'user_role' in session:
            return redirect(url_for(f"{session['user_role']}_dashboard"))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not all([username, password]):
                flash('Por favor ingresa usuario y contraseña', 'danger')
                return render_template('auth/login.html')
            
            # Usar el método corregido con mysql como primer parámetro
            usuario_data = Usuario.validar_credenciales(mysql, username, password)
            
            if usuario_data:
                # Configurar sesión usando los datos del diccionario
                session['user_id'] = usuario_data['id']
                session['user_role'] = usuario_data['rol']
                session['user_name'] = usuario_data['usuario']
                session.permanent = True
                
                return redirect(url_for(f"{usuario_data['rol']}_dashboard"))
            else:
                flash('Usuario o contraseña incorrectos', 'danger')
        
        return render_template('auth/login.html')

    @staticmethod
    def api_login():
        """API endpoint para login (JSON)"""
        try:
            # Importar mysql desde app
            from app import mysql
            
            # Verificar que es una petición JSON
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Content-Type debe ser application/json'
                }), 400
            
            # Si ya está autenticado
            if 'user_id' in session and 'user_role' in session:
                return jsonify({
                    'success': True,
                    'message': 'Ya está autenticado',
                    'role': session['user_role'],
                    'user_id': session['user_id'],
                    'user_name': session['user_name']
                })
            
            datos = request.get_json()
            username = datos.get('usuario')  # Coincide con el JS
            password = datos.get('password')
            
            # Validar campos requeridos
            if not username or not password:
                return jsonify({
                    'success': False,
                    'message': 'Usuario y contraseña son requeridos'
                }), 400
            
            # Validar credenciales usando el método corregido
            usuario_data = Usuario.validar_credenciales(mysql, username.strip(), password)
            
            if usuario_data:
                # Configurar sesión usando los datos del diccionario
                session['user_id'] = usuario_data['id']
                session['user_role'] = usuario_data['rol']
                session['user_name'] = usuario_data['usuario']
                session.permanent = True
                
                return jsonify({
                    'success': True,
                    'message': f'Bienvenido, {usuario_data["usuario"]}',
                    'role': usuario_data['rol'],
                    'user_id': usuario_data['id'],
                    'user_name': usuario_data['usuario']
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Usuario o contraseña incorrectos'
                }), 401
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error interno del servidor: {str(e)}'
            }), 500

    @staticmethod
    def check_session():
        """API para verificar si hay una sesión activa"""
        try:
            if 'user_id' in session and 'user_role' in session:
                return jsonify({
                    'authenticated': True,
                    'role': session['user_role'],
                    'user_id': session['user_id'],
                    'user_name': session['user_name']
                })
            else:
                return jsonify({
                    'authenticated': False
                })
        except Exception as e:
            return jsonify({
                'authenticated': False,
                'error': str(e)
            }), 500

    @staticmethod
    def logout():
        """Cierra la sesión del usuario"""
        user_name = session.get('user_name', 'Usuario')
        session.clear()
        
        # Si es petición AJAX, retornar JSON
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'success': True,
                'message': f'Sesión cerrada, {user_name}.'
            })
        
        # Si es petición normal, flash y redirect
        flash(f'Sesión cerrada, {user_name}.', 'info')
        return redirect(url_for('login'))

    @staticmethod
    def forgot_password():
        """Endpoint para recuperación de contraseña (temporal)"""
        try:
            from app import mysql
            
            if request.method == 'POST':
                if request.is_json:
                    datos = request.get_json()
                    username = datos.get('usuario')
                else:
                    username = request.form.get('usuario')
                
                if not username:
                    response_data = {
                        'success': False,
                        'message': 'El campo usuario es requerido'
                    }
                    return jsonify(response_data) if request.is_json else render_template('auth/forgot_password.html', error=response_data['message'])
                
                # Verificar si el usuario existe usando consulta SQL directa
                try:
                    cursor = mysql.connection.cursor()
                    query = "SELECT id, usuario FROM usuarios WHERE usuario = %s AND activo = 1"
                    cursor.execute(query, (username.strip(),))
                    usuario = cursor.fetchone()
                    cursor.close()
                    
                    if usuario:
                        # TODO: Implementar envío de email real
                        # Por ahora solo simular el proceso
                        response_data = {
                            'success': True,
                            'message': f'Se ha enviado un enlace de recuperación al correo registrado para {username}'
                        }
                    else:
                        response_data = {
                            'success': False,
                            'message': 'Usuario no encontrado'
                        }
                except Exception as e:
                    response_data = {
                        'success': False,
                        'message': f'Error al verificar usuario: {str(e)}'
                    }
                
                return jsonify(response_data) if request.is_json else render_template('auth/forgot_password.html', message=response_data['message'])
            
            return render_template('auth/forgot_password.html')
            
        except Exception as e:
            error_msg = f'Error interno: {str(e)}'
            return jsonify({'success': False, 'message': error_msg}) if request.is_json else render_template('auth/forgot_password.html', error=error_msg)