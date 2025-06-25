from flask import Flask, render_template, url_for, request, redirect, flash, jsonify, session
from flask_mysqldb import MySQL
from functools import wraps
from config.config import Config
from datetime import datetime, date
from controllers.inicio_sesion import AuthController

# ########################################################
from controllers.admin_dashboard import (
    obtener_resumen_dashboard, 
    obtener_pacientes_recientes, 
    obtener_citas_hoy
)
from controllers.admin_pacientes import (
    obtener_pacientes,
    obtener_pacientes_con_filtros, 
    obtener_medicos_para_asignacion,
    crear_nuevo_paciente,
    obtener_paciente_por_id,
    actualizar_paciente,
    cambiar_estado_paciente,
    asignar_cuidador_a_paciente
)

from controllers.admin_profesionales import (
    obtener_profesionales,
    obtener_profesionales_con_filtros,
    obtener_profesional_por_id,
    crear_nuevo_profesional,
    actualizar_profesional,
    cambiar_estado_profesional,
    obtener_estadisticas_profesionales
)

from controllers.admin_horarios import (
    obtener_horarios_semana,
    obtener_medicos_activos,
    crear_horario_disponible,
    obtener_detalle_horario,
    eliminar_horario_disponible,
    obtener_estadisticas_horarios,
    actualizar_horario_disponible
)

from controllers.paciente_citas import (
    crear_cita_paciente,
    obtener_cita_paciente,
    cancelar_cita_paciente,
    listar_citas_paciente,
    obtener_resumen_dashboard_paciente
)

from controllers.admin_citas_medicas import (
    obtener_citas_medicas,
    obtener_citas_con_filtros,
    obtener_medicos_para_filtro,
    obtener_estadisticas_citas,
    obtener_detalle_cita,
    cancelar_cita_admin,
    actualizar_estado_cita
)

# ==============================================================================
# INICIALIZACIÓN DE LA APLICACIÓN
# ==============================================================================
app = Flask(__name__)
app.config.from_object(Config)

# Inicializar MySQL con Flask-MySQLdb
mysql = MySQL(app)

# ==============================================================================
# DECORADORES DE AUTENTICACIÓN
# ==============================================================================

def login_required(f):
    """Decorador para rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or 'user_role' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """Decorador para rutas que requieren roles específicos"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session:
                flash('Debes iniciar sesión para acceder a esta página.', 'warning')
                return redirect(url_for('login'))
            
            if session['user_role'] not in allowed_roles:
                flash('No tienes permisos para acceder a esta página.', 'danger')
                return redirect(url_for(f"{session['user_role']}_dashboard"))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==============================================================================
# RUTAS DE AUTENTICACIÓN
# ==============================================================================

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    """Maneja el proceso de inicio de sesión (web tradicional)"""
    return AuthController.procesar_login()

@app.route('/api/auth/desktop-login', methods=['POST'])
def api_desktop_login():
    """API endpoint para login desde desktop (JSON)"""
    return AuthController.api_login()

@app.route('/api/auth/check-professional-session', methods=['GET'])
def api_check_session():
    """API para verificar sesión activa"""
    return AuthController.check_session()

@app.route('/api/auth/forgot-password-professional', methods=['GET', 'POST'])
def api_forgot_password():
    """API para recuperación de contraseña"""
    return AuthController.forgot_password()

@app.route('/logout')
def logout():
    """Maneja el cierre de sesión"""
    return AuthController.logout()

@app.route('/auth/forgot_password')
def forgot_password():
    """Recuperación de contraseña (web tradicional)"""
    return render_template('auth/forgot_password.html')

@app.route('/')
def home():
    """Redirige al login o dashboard según autenticación"""
    if 'user_id' in session and 'user_role' in session:
        return redirect(url_for(f"{session['user_role']}_dashboard"))
    return redirect(url_for('login'))

@app.route('/auth/desktop')
def desktop_login():
    """Página de login para escritorio"""
    return render_template('auth/login_desktop.html')

# ==============================================================================
# RUTAS PARA ADMINISTRADOR (PROTEGIDAS)
# ==============================================================================

@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    """Panel principal de administración."""
    resumen_info = obtener_resumen_dashboard()
    pacientes_recientes = obtener_pacientes_recientes()
    citas_de_hoy = obtener_citas_hoy()
    return render_template('admin/dashboard.html', 
                           resumen_info=resumen_info, 
                           pacientes_recientes=pacientes_recientes, 
                           citas_de_hoy=citas_de_hoy)

@app.route('/admin/pacientes')
# @login_required
# @role_required('admin')
def admin_pacientes():
    """Gestión de pacientes (listado/edición)"""
    pacientes = obtener_pacientes()
    return render_template('admin/pacientes.html', pacientes=pacientes)

# ==============================================================================
# API PARA GESTIÓN DE PACIENTES (ADMIN - PROTEGIDAS)
# ==============================================================================

@app.route('/admin/pacientes/api/listar')
@login_required
@role_required('admin')
def admin_pacientes_api():
    """API para obtener pacientes con filtros y paginación"""
    estado = request.args.get('estado', 'todos')
    medico_id = request.args.get('medico_id', 'todos')
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    busqueda = request.args.get('busqueda', '').strip()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    if not busqueda:
        busqueda = None
    if fecha_desde == '':
        fecha_desde = None
    if fecha_hasta == '':
        fecha_hasta = None
    if medico_id == 'todos':
        medico_id = None
    
    resultado = obtener_pacientes_con_filtros(
        estado=estado,
        medico_id=medico_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        busqueda=busqueda,
        page=page,
        per_page=per_page
    )
    
    return jsonify(resultado)

@app.route('/admin/pacientes/api/medicos', methods=['GET']) 
# @login_required
# @role_required('admin')
def admin_pacientes_medicos_api():
    """API para obtener lista de médicos para asignación"""
    medicos = obtener_medicos_para_asignacion()
    return jsonify({'medicos': medicos})

@app.route('/admin/pacientes/api/crear', methods=['POST'])
@login_required
@role_required('admin')
def admin_pacientes_crear_api(): 
    """API para crear un nuevo paciente"""
    datos = request.get_json()
    resultado = crear_nuevo_paciente(datos)
    return jsonify(resultado)

@app.route('/admin/pacientes/api/<int:paciente_id>')
@login_required
@role_required('admin')
def admin_pacientes_detalle_api(paciente_id):
    """API para obtener detalles de un paciente específico"""
    paciente = obtener_paciente_por_id(paciente_id)
    if paciente:
        return jsonify({'success': True, 'paciente': paciente})
    else:
        return jsonify({'success': False, 'message': 'Paciente no encontrado'}), 404

@app.route('/admin/pacientes/api/<int:paciente_id>/actualizar', methods=['PUT'])
@login_required
@role_required('admin')
def admin_pacientes_actualizar_api(paciente_id):
    """API para actualizar datos de un paciente"""
    datos = request.get_json()
    resultado = actualizar_paciente(paciente_id, datos)
    return jsonify(resultado)

@app.route('/admin/pacientes/api/<int:paciente_id>/toggle-estado', methods=['POST'])
@login_required
@role_required('admin')
def admin_pacientes_toggle_estado_api(paciente_id):
    """API para cambiar estado del paciente (ACTIVO/INACTIVO)"""
    resultado = cambiar_estado_paciente(paciente_id)
    return jsonify(resultado)

@app.route('/admin/pacientes/api/<int:paciente_id>/asignar-cuidador', methods=['POST'])
@login_required
@role_required('admin')
def admin_pacientes_asignar_cuidador_api(paciente_id):
    """API para asignar cuidador a un paciente"""
    datos = request.get_json()
    resultado = asignar_cuidador_a_paciente(paciente_id, datos)
    return jsonify(resultado)

# ==============================================================================
# RUTAS PARA GESTIÓN DE PROFESIONALES (ADMIN - PROTEGIDAS)
# ==============================================================================

@app.route('/admin/profesionales')
@login_required
@role_required('admin')
def admin_profesionales():
    """Gestión de profesionales médicos"""
    profesionales = obtener_profesionales()
    return render_template('admin/profesionales.html', profesionales=profesionales)

@app.route('/admin/profesionales/api/listar')
@login_required
@role_required('admin')
def admin_profesionales_api():
    """API para obtener profesionales con filtros y paginación"""
    especialidad = request.args.get('especialidad', 'todas')
    rol = request.args.get('rol', 'todos')
    estado = request.args.get('estado', 'todos')
    busqueda = request.args.get('busqueda', '').strip()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    if not busqueda:
        busqueda = None
    
    resultado = obtener_profesionales_con_filtros(
        especialidad=especialidad,
        rol=rol,
        estado=estado,
        busqueda=busqueda,
        page=page,
        per_page=per_page
    )
    
    return jsonify(resultado)

@app.route('/admin/profesionales/api/crear', methods=['POST'])
@login_required
@role_required('admin')
def admin_profesionales_crear_api():
    """API para crear un nuevo profesional"""
    datos = request.get_json()
    resultado = crear_nuevo_profesional(datos)
    return jsonify(resultado)

@app.route('/admin/profesionales/api/<int:profesional_id>')
@login_required
@role_required('admin')
def admin_profesionales_detalle_api(profesional_id):
    """API para obtener detalles de un profesional específico"""
    profesional = obtener_profesional_por_id(profesional_id)
    if profesional:
        return jsonify({'success': True, 'profesional': profesional})
    else:
        return jsonify({'success': False, 'message': 'Profesional no encontrado'}), 404

@app.route('/admin/profesionales/api/<int:profesional_id>/actualizar', methods=['PUT'])
@login_required
@role_required('admin')
def admin_profesionales_actualizar_api(profesional_id):
    """API para actualizar datos de un profesional"""
    datos = request.get_json()
    resultado = actualizar_profesional(profesional_id, datos)
    return jsonify(resultado)

@app.route('/admin/profesionales/api/<int:profesional_id>/toggle-estado', methods=['POST'])
@login_required
@role_required('admin')
def admin_profesionales_toggle_estado_api(profesional_id):
    """API para cambiar estado del profesional (ACTIVO/INACTIVO)"""
    resultado = cambiar_estado_profesional(profesional_id)
    return jsonify(resultado)

@app.route('/admin/profesionales/api/estadisticas')
@login_required
@role_required('admin')
def admin_profesionales_estadisticas_api():
    """API para obtener estadísticas de profesionales"""
    estadisticas = obtener_estadisticas_profesionales()
    return jsonify(estadisticas)

# ==============================================================================
# RUTAS PARA GESTIÓN DE HORARIOS (ADMIN - PROTEGIDAS)
# ==============================================================================

@app.route('/admin/horarios')
@login_required
@role_required('admin')
def admin_horarios():
    """Panel principal de gestión de horarios disponibles."""
    profesionales_activos = obtener_medicos_activos()
    datos_semana_actual = obtener_horarios_semana()
    estadisticas_horarios = obtener_estadisticas_horarios()
    
    return render_template('admin/horarios.html',
                         profesionales_activos=profesionales_activos,
                         datos_semana=datos_semana_actual,
                         estadisticas=estadisticas_horarios)

@app.route('/admin/citas')
@login_required
@role_required('admin')
def admin_citas():
    """Gestión del calendario de citas médicas."""
    profesionales_activos = obtener_medicos_activos()
    citas_recientes = obtener_citas_hoy()
    estadisticas_citas = obtener_estadisticas_citas()
    
    return render_template('admin/citas.html',
                         profesionales_activos=profesionales_activos,
                         citas_recientes=citas_recientes,
                         estadisticas=estadisticas_citas)

@app.route('/admin/citas/api/listar')
@login_required
@role_required('admin')
def admin_citas_listar_api():
    """API para obtener citas médicas con filtros y paginación."""
    try:
        fecha = request.args.get('fecha', 'todas')
        medico_id = request.args.get('medico_id', 'todos')
        especialidad = request.args.get('especialidad', 'todas')
        estado = request.args.get('estado', 'todos')
        tipo = request.args.get('tipo', 'todos')
        busqueda = request.args.get('busqueda', '').strip()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        if not busqueda:
            busqueda = None
        if fecha == 'todas':
            fecha = None
        if medico_id == 'todos':
            medico_id = None
        
        resultado = obtener_citas_con_filtros(
            fecha=fecha,
            medico_id=medico_id,
            especialidad=especialidad,
            estado=estado,
            tipo=tipo,
            busqueda=busqueda,
            page=page,
            per_page=per_page
        )
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': f'Error interno: {str(e)}',
            'citas': [],
            'pagination': {}
        }), 500

@app.route('/admin/citas/api/medicos')
@login_required
@role_required('admin')
def admin_citas_medicos_api():
    """API para obtener lista de médicos para filtros."""
    try:
        medicos = obtener_medicos_para_filtro()
        return jsonify({
            'exito': True,
            'medicos': medicos
        })
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': f'Error interno: {str(e)}',
            'medicos': []
        }), 500

@app.route('/admin/citas/api/estadisticas')
@login_required
@role_required('admin')
def admin_citas_estadisticas_api():
    """API para obtener estadísticas de citas médicas."""
    try:
        estadisticas = obtener_estadisticas_citas()
        return jsonify({
            'exito': True,
            'estadisticas': estadisticas
        })
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': f'Error interno: {str(e)}',
            'estadisticas': {}
        }), 500

@app.route('/admin/citas/api/<int:cita_id>')
@login_required
@role_required('admin')
def admin_citas_detalle_api(cita_id):
    """API para obtener detalles de una cita específica."""
    try:
        resultado = obtener_detalle_cita(cita_id)
        
        if resultado['exito']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 404
            
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }), 500

@app.route('/admin/citas/api/<int:cita_id>/cancelar', methods=['POST'])
@login_required
@role_required('admin')
def admin_citas_cancelar_api(cita_id):
    """API para cancelar una cita médica."""
    try:
        resultado = cancelar_cita_admin(cita_id)
        
        if resultado['exito']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }), 500

@app.route('/admin/citas/api/<int:cita_id>/estado', methods=['PUT'])
@login_required
@role_required('admin')
def admin_citas_actualizar_estado_api(cita_id):
    """API para actualizar el estado de una cita."""
    try:
        if not request.is_json:
            return jsonify({
                'exito': False,
                'error': 'Content-Type debe ser application/json'
            }), 400
        
        datos = request.get_json()
        nuevo_estado = datos.get('estado')
        
        if not nuevo_estado:
            return jsonify({
                'exito': False,
                'error': 'El campo estado es requerido'
            }), 400
        
        resultado = actualizar_estado_cita(cita_id, nuevo_estado)
        
        if resultado['exito']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }), 500

@app.route('/admin/citas/api/hoy')
@login_required
@role_required('admin')
def admin_citas_hoy_api():
    """API para obtener las citas del día actual."""
    try:
        citas_hoy = obtener_citas_hoy()
        return jsonify({
            'exito': True,
            'citas': citas_hoy,
            'total': len(citas_hoy)
        })
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': f'Error interno: {str(e)}',
            'citas': [],
            'total': 0
        }), 500

# ==============================================================================
# API PARA GESTIÓN DE HORARIOS (ADMIN - PROTEGIDAS)
# ==============================================================================

@app.route('/admin/horarios/semana')
@login_required
@role_required('admin')
def api_obtener_horarios_semana():
    """API para obtener horarios de una semana específica."""
    try:
        fecha_str = request.args.get('fecha')
        fecha_referencia = None
        
        if fecha_str:
            fecha_referencia = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        
        datos_semana = obtener_horarios_semana(fecha_referencia)
        
        return jsonify({
            'exito': True,
            'lunes': datos_semana['lunes'].isoformat(),
            'viernes': datos_semana['viernes'].isoformat(),
            'datos_dias': {
                fecha: {
                    'fecha': datos['fecha'].isoformat() if isinstance(datos['fecha'], date) else datos['fecha'],
                    'nombre_dia': datos['nombre_dia'],
                    'horarios': datos['horarios']
                }
                for fecha, datos in datos_semana['datos_dias'].items()
            }
        })
        
    except ValueError as ve:
        return jsonify({
            'exito': False,
            'error': f'Formato de fecha inválido. Use YYYY-MM-DD. Error: {str(ve)}'
        }), 400
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }), 500

@app.route('/admin/horarios/crear', methods=['POST'])
@login_required
@role_required('admin')
def api_crear_horario():
    """API para crear un nuevo horario disponible."""
    try:
        if not request.is_json:
            return jsonify({
                'exito': False,
                'error': 'Se requiere contenido JSON'
            }), 400
        
        datos_horario = request.get_json()
        resultado = crear_horario_disponible(datos_horario)
        
        if resultado['exito']:
            return jsonify(resultado), 201
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }), 500

@app.route('/admin/horarios/<int:horario_id>')
@login_required
@role_required('admin')
def api_obtener_detalle_horario(horario_id):
    """API para obtener detalles de un horario específico."""
    try:
        resultado = obtener_detalle_horario(horario_id)
        
        if resultado['exito']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 404
            
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }), 500

@app.route('/admin/horarios/<int:horario_id>/actualizar', methods=['PUT'])
@login_required
@role_required('admin')
def api_actualizar_horario(horario_id):
    """API para actualizar un horario disponible existente."""
    try:
        if not request.is_json:
            return jsonify({
                'exito': False,
                'error': 'Se requiere contenido JSON'
            }), 400
        
        datos_horario = request.get_json()
        datos_horario['horario_id'] = horario_id
        
        resultado = actualizar_horario_disponible(datos_horario)
        
        if resultado['exito']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }), 500

@app.route('/admin/horarios/<int:horario_id>/eliminar', methods=['DELETE'])
@login_required
@role_required('admin')
def api_eliminar_horario(horario_id):
    """API para eliminar un horario disponible."""
    try:
        resultado = eliminar_horario_disponible(horario_id)
        
        if resultado['exito']:
            return jsonify(resultado)   
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }), 500

@app.route('/admin/profesionales/activos')
@login_required
@role_required('admin')
def api_obtener_profesionales_activos():
    """API para obtener lista de profesionales activos."""
    try:
        profesionales = obtener_medicos_activos()
        
        return jsonify({
            'exito': True,
            'profesionales': profesionales
        })
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }), 500

@app.route('/admin/horarios/estadisticas')
@login_required
@role_required('admin')
def api_obtener_estadisticas_horarios():
    """API para obtener estadísticas del sistema de horarios."""
    try:
        estadisticas = obtener_estadisticas_horarios()
        
        return jsonify({
            'exito': True,
            'estadisticas': estadisticas
        })
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }), 500

# ==============================================================================
# RUTAS PARA OTROS ROLES (PROTEGIDAS)
# ==============================================================================

@app.route('/medico/dashboard')
@login_required
@role_required('medico')
def medico_dashboard():
    """Panel principal para médicos"""
    return render_template('medico/dashboard.html')

@app.route('/psicologo/dashboard')
@login_required
@role_required('psicologo')
def psicologo_dashboard():
    """Panel principal para psicólogos"""
    return render_template('psicologo/dashboard.html')

# ======================
# Rutas para Paciente
# ======================
@app.route('/paciente/dashboard')
def paciente_dashboard():
    return render_template('paciente/dashboard.html')
########################
from controllers.registro_triaje import biometrico_bp
app.register_blueprint(biometrico_bp)

@app.route('/paciente/datos_biometricos')
def paciente_datos_biometricos():
    return redirect(url_for('triaje.datos_biometricos'))

from controllers.registro_infoadicional import infoadicional_bp
app.register_blueprint(infoadicional_bp)

@app.route('/paciente/actividad_fisica')
def paciente_actividad_fisica():
    return redirect(url_for('infoadicional.informacion_adicional'))

from controllers.lista_medicamentos import medicamentos_bp
app.register_blueprint(medicamentos_bp)

@app.route('/paciente/medicamentos')
def paciente_medicamentos():
    return redirect(url_for('medicamentos.listar_medicamentos'))

from controllers.lista_alertascritica import alertas_bp
app.register_blueprint(alertas_bp)

@app.route('/paciente/alertas_criticas')
def paciente_alertas_criticas():
    return redirect(url_for('alertas.listar_alertascritica'))

@app.route('/paciente/cita')
def paciente_cita():
    return render_template('paciente/cita.html')

@app.route('/paciente/educacion_en_salud')
def paciente_educacion_en_salud():
    return render_template('paciente/educacionSalud.html')

@app.route('/paciente/foro')
def paciente_foro():
    return render_template('paciente/foro.html')

# ======================
# Rutas para Paramedico
# ======================
from controllers.lista_alertascriticaParamedico import paramedico_bp
app.register_blueprint(paramedico_bp)

@app.route('/paramedico/alertas_criticas')
def paramedico_alertas_criticas():
    return redirect(url_for('paramedico.alertas'))

@app.route('/paramedico/agregar_nota_alerta')
def paramedico_agregar_nota():
    return redirect(url_for('paramedico.agregar_nota_alerta'))

@app.route('/paramedico/dashboard')
def paramedico_dashboard():
    return render_template('paramedico/dashboard.html')

# ==============================================================================
# API PARA CUIDADORES (EJEMPLO)
# ==============================================================================

@app.route('/cuidador/dashboard')
@login_required
@role_required('cuidador')
def cuidador_dashboard():
    """Panel principal para cuidadores"""
    return render_template('cuidador/dashboard.html')

# ==============================================================================
# API PARA CREAR CITAS (EJEMPLO)
# ==============================================================================

@app.route('/admin/citas/crear', methods=['POST'])
@login_required
@role_required('admin', 'paciente')
def paciente_crear_cita_api():
    """API para crear una nueva cita."""
    try:
        if not request.is_json:
            return jsonify({
                'exito': False,
                'error': 'Content-Type debe ser application/json'
            }), 400
        
        datos = request.get_json()
        if not datos:
            return jsonify({
                'exito': False,
                'error': 'Body vacío'
            }), 400
        
        resultado = crear_cita_paciente(datos)
        
        if resultado['exito']:
            return jsonify(resultado), 201
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }), 500

# ==============================================================================
# EJECUCIÓN PRINCIPAL
# ==============================================================================

if __name__ == '__main__':
    app.run(debug=True)