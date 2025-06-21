from flask import render_template, redirect, url_for, flash, request, session
from models.login import Usuario

class AuthController:
    @staticmethod
    def procesar_login():
        """Procesa el formulario de login"""
        # Si ya está autenticado, redirigir
        if 'user_id' in session and 'user_role' in session:
            return redirect(url_for(f"{session['user_role']}_dashboard"))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not all([username, password]):
                flash('Por favor ingresa usuario y contraseña', 'danger')
                return render_template('auth/login.html')
            
            usuario = Usuario.validar_credenciales(username, password)
            
            if usuario:
                # Configurar sesión
                session['user_id'] = usuario.id
                session['user_role'] = usuario.rol
                session['user_name'] = usuario.usuario
                session.permanent = True
                
                flash(f'Bienvenido, {usuario.usuario}!', 'success')
                return redirect(url_for(f"{usuario.rol}_dashboard"))
            else:
                flash('Usuario o contraseña incorrectos', 'danger')
        
        return render_template('auth/login.html')

    @staticmethod
    def logout():
        """Cierra la sesión del usuario"""
        user_name = session.get('user_name', 'Usuario')
        session.clear()
        flash(f'Sesión cerrada, {user_name}.', 'info')
        return redirect(url_for('login'))