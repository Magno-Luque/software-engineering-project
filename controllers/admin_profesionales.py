# controllers/admin_profesionales.py

from models.actores import db, Paciente, Profesional, Cuidador, PacienteEnfermedadMedico, Enfermedad
from datetime import datetime, date
from sqlalchemy import or_, desc, func
import re
import json

def obtener_profesionales():
    """
    Obtiene todos los profesionales con datos básicos para la vista principal
    """
    profesionales = Profesional.query.filter(Profesional.estado == 'ACTIVO').all()
    
    resultado = []
    for prof in profesionales:
        # Contar pacientes asignados desde la tabla intermedia
        pacientes_asignados = db.session.query(PacienteEnfermedadMedico)\
            .filter(PacienteEnfermedadMedico.medico_id == prof.id)\
            .filter(PacienteEnfermedadMedico.estado == 'ACTIVO')\
            .count()
        
        # Formatear horarios
        horario_formateado = formatear_horario_atencion(prof.horario_atencion)
        
        resultado.append({
            'id': prof.id,
            'nombre_completo': f"{prof.nombres} {prof.apellidos}",
            'dni': prof.dni,
            'especialidad': prof.especialidad,
            'rol': prof.rol,
            'horario_atencion': horario_formateado,
            'pacientes_asignados': pacientes_asignados,
            'email': prof.email,
            'telefono': prof.telefono,
            'estado': prof.estado,
            'fecha_registro': prof.fecha_registro.strftime('%d/%m/%Y') if prof.fecha_registro else 'No registrada'
        })
    
    return resultado

def obtener_profesionales_con_filtros(especialidad=None, rol=None, estado=None, busqueda=None, page=1, per_page=10):
    """
    Obtiene profesionales aplicando filtros y paginación
    """
    query = Profesional.query
    
    # Filtro por especialidad
    if especialidad and especialidad != 'todas':
        especialidad_map = {
            'cardiologia': 'CARDIOLOGÍA',
            'medicina-interna': 'MEDICINA INTERNA',
            'endocrinologia': 'ENDOCRINOLOGÍA',
            'psicologia': 'PSICOLOGÍA CLÍNICA',
            'neumologia': 'NEUMOLOGÍA'
        }
        if especialidad in especialidad_map:
            query = query.filter(Profesional.especialidad == especialidad_map[especialidad])
    
    # Filtro por rol
    if rol and rol != 'todos':
        rol_map = {
            'medico': 'MÉDICO',
            'psicologo': 'PSICÓLOGO'
        }
        if rol in rol_map:
            query = query.filter(Profesional.rol == rol_map[rol])
    
    # Filtro por estado
    if estado and estado != 'todos':
        query = query.filter(Profesional.estado == estado.upper())
    
    # Filtro de búsqueda (nombre o DNI)
    if busqueda:
        busqueda_like = f"%{busqueda}%"
        query = query.filter(
            or_(
                Profesional.nombres.ilike(busqueda_like),
                Profesional.apellidos.ilike(busqueda_like),
                Profesional.dni.like(busqueda_like)
            )
        )
    
    # Ordenar por fecha de registro descendente
    query = query.order_by(desc(Profesional.fecha_registro))
    
    # Aplicar paginación
    resultado = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Formatear datos para la vista
    profesionales_formateados = []
    for prof in resultado.items:
        # Contar pacientes asignados
        pacientes_asignados = db.session.query(PacienteEnfermedadMedico)\
            .filter(PacienteEnfermedadMedico.medico_id == prof.id)\
            .filter(PacienteEnfermedadMedico.estado == 'ACTIVO')\
            .count()
        
        profesionales_formateados.append({
            'id': prof.id,
            'nombre_completo': f"{prof.nombres} {prof.apellidos}",
            'dni': prof.dni,
            'especialidad': prof.especialidad,
            'rol': prof.rol,
            'horario_atencion': formatear_horario_atencion(prof.horario_atencion),
            'pacientes_asignados': pacientes_asignados,
            'email': prof.email,
            'telefono': prof.telefono,
            'estado': prof.estado,
            'fecha_registro': prof.fecha_registro.strftime('%d/%m/%Y') if prof.fecha_registro else 'No registrada'
        })
    
    return {
        'profesionales': profesionales_formateados,
        'total': resultado.total,
        'pages': resultado.pages,
        'current_page': resultado.page,
        'per_page': resultado.per_page,
        'has_prev': resultado.has_prev,
        'has_next': resultado.has_next
    }

def obtener_profesional_por_id(profesional_id):
    """
    Obtiene datos completos de un profesional específico
    """
    profesional = Profesional.query.get(profesional_id)
    if not profesional:
        return None
    
    # Obtener pacientes asignados con detalles
    pacientes_asignados = db.session.query(
        PacienteEnfermedadMedico, Paciente, Enfermedad
    ).join(
        Paciente, PacienteEnfermedadMedico.paciente_id == Paciente.id
    ).join(
        Enfermedad, PacienteEnfermedadMedico.enfermedad_id == Enfermedad.id
    ).filter(
        PacienteEnfermedadMedico.medico_id == profesional_id
    ).filter(
        PacienteEnfermedadMedico.estado == 'ACTIVO'
    ).all()
    
    # Formatear pacientes asignados
    pacientes_detalle = []
    for asignacion, paciente, enfermedad in pacientes_asignados:
        pacientes_detalle.append({
            'id': paciente.id,
            'nombre_completo': f"{paciente.nombres} {paciente.apellidos}",
            'dni': paciente.dni,
            'enfermedad': enfermedad.nombre,
            'fecha_asignacion': asignacion.fecha_asignacion.strftime('%d/%m/%Y'),
            'observaciones': asignacion.observaciones
        })
    
    return {
        'id': profesional.id,
        'dni': profesional.dni,
        'nombres': profesional.nombres,
        'apellidos': profesional.apellidos,
        'nombre_completo': f"{profesional.nombres} {profesional.apellidos}",
        'especialidad': profesional.especialidad,
        'rol': profesional.rol,
        'telefono': profesional.telefono,
        'email': profesional.email,
        'horario_atencion': profesional.horario_atencion,
        'pacientes_asignados_count': len(pacientes_detalle),
        'pacientes_asignados': pacientes_detalle,
        'estado': profesional.estado,
        'fecha_registro': profesional.fecha_registro.strftime('%d/%m/%Y %H:%M') if profesional.fecha_registro else 'No registrada'
    }

def crear_nuevo_profesional(datos):
    """
    Crea un nuevo profesional con los datos proporcionados
    """
    try:
        # Validar que el DNI no exista
        profesional_existente = Profesional.query.filter_by(dni=datos['dni']).first()
        if profesional_existente:
            return {
                'success': False,
                'message': 'Ya existe un profesional con este DNI'
            }
        
        # Validar que el email no exista
        email_existente = Profesional.query.filter_by(email=datos['email']).first()
        if email_existente:
            return {
                'success': False,
                'message': 'Ya existe un profesional con este email'
            }
        
        # Procesar horarios de atención
        horarios = procesar_horarios_atencion(datos.get('horarios', {}))
        
        # Crear el profesional
        nuevo_profesional = Profesional(
            dni=datos['dni'],
            nombres=datos['nombres'],
            apellidos=datos['apellidos'],
            especialidad=datos['especialidad'],
            rol=datos['rol'],
            telefono=datos.get('telefono'),
            email=datos['email'],
            horario_atencion=horarios,
            estado='ACTIVO'
        )
        
        db.session.add(nuevo_profesional)
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Profesional creado exitosamente',
            'profesional_id': nuevo_profesional.id
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'Error al crear profesional: {str(e)}'
        }

def actualizar_profesional(profesional_id, datos):
    """
    Actualiza los datos de un profesional existente
    """
    try:
        profesional = Profesional.query.get(profesional_id)
        if not profesional:
            return {'success': False, 'message': 'Profesional no encontrado'}
        
        # Validar DNI único (excluyendo el profesional actual)
        dni_existente = Profesional.query.filter(
            Profesional.dni == datos['dni'],
            Profesional.id != profesional_id
        ).first()
        if dni_existente:
            return {'success': False, 'message': 'El DNI ya está registrado por otro profesional'}
        
        # Validar email único (excluyendo el profesional actual)
        email_existente = Profesional.query.filter(
            Profesional.email == datos['email'],
            Profesional.id != profesional_id
        ).first()
        if email_existente:
            return {'success': False, 'message': 'El email ya está registrado por otro profesional'}
        
        # Actualizar campos
        profesional.dni = datos.get('dni', profesional.dni)
        profesional.nombres = datos.get('nombres', profesional.nombres)
        profesional.apellidos = datos.get('apellidos', profesional.apellidos)
        profesional.especialidad = datos.get('especialidad', profesional.especialidad)
        profesional.rol = datos.get('rol', profesional.rol)
        profesional.telefono = datos.get('telefono', profesional.telefono)
        profesional.email = datos.get('email', profesional.email)
        
        # Actualizar horarios si se proporcionan
        if 'horarios' in datos:
            horarios = procesar_horarios_atencion(datos['horarios'])
            profesional.horario_atencion = horarios
        
        db.session.commit()
        
        return {'success': True, 'message': 'Profesional actualizado exitosamente'}
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Error al actualizar profesional: {str(e)}'}

def cambiar_estado_profesional(profesional_id):
    """
    Cambia el estado de un profesional entre ACTIVO/INACTIVO
    """
    try:
        profesional = Profesional.query.get(profesional_id)
        if not profesional:
            return {'success': False, 'message': 'Profesional no encontrado'}
        
        # Cambiar estado
        nuevo_estado = 'INACTIVO' if profesional.estado == 'ACTIVO' else 'ACTIVO'
        profesional.estado = nuevo_estado
        
        db.session.commit()
        
        return {
            'success': True,
            'message': f'Estado del profesional cambiado a {nuevo_estado}',
            'nuevo_estado': nuevo_estado
        }
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Error al cambiar estado: {str(e)}'}

def obtener_estadisticas_profesionales():
    """
    Obtiene estadísticas generales de profesionales
    """
    total_profesionales = Profesional.query.count()
    profesionales_activos = Profesional.query.filter_by(estado='ACTIVO').count()
    
    # Estadísticas por especialidad
    especialidades = db.session.query(
        Profesional.especialidad,
        func.count(Profesional.id).label('count')
    ).group_by(Profesional.especialidad).all()
    
    # Estadísticas por rol
    roles = db.session.query(
        Profesional.rol,
        func.count(Profesional.id).label('count')
    ).group_by(Profesional.rol).all()
    
    return {
        'total_profesionales': total_profesionales,
        'profesionales_activos': profesionales_activos,
        'profesionales_inactivos': total_profesionales - profesionales_activos,
        'por_especialidad': [{'especialidad': esp, 'count': count} for esp, count in especialidades],
        'por_rol': [{'rol': rol, 'count': count} for rol, count in roles]
    }

# Funciones auxiliares

def formatear_horario_atencion(horario_json):
    """
    Convierte el JSON de horarios en texto legible
    """
    if not horario_json:
        return "No definido"
    
    try:
        if isinstance(horario_json, str):
            horarios = json.loads(horario_json)
        else:
            horarios = horario_json
        
        dias_formateados = []
        dias_semana = {
            'lunes': 'Lunes',
            'martes': 'Martes',
            'miercoles': 'Miércoles',
            'jueves': 'Jueves',
            'viernes': 'Viernes',
            'sabado': 'Sábado',
            'domingo': 'Domingo'
        }
        
        for dia, horario in horarios.items():
            if horario and horario != 'No disponible':
                dia_nombre = dias_semana.get(dia.lower(), dia)
                dias_formateados.append(f"{dia_nombre}: {horario}")
        
        return '; '.join(dias_formateados) if dias_formateados else "No definido"
        
    except (json.JSONDecodeError, TypeError):
        return "Formato inválido"

def procesar_horarios_atencion(horarios_data):
    """
    Procesa los datos de horarios del formulario y los convierte a JSON
    """
    horarios = {}
    
    dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
    
    for dia in dias:
        activo = horarios_data.get(f'{dia}_activo', False)
        if activo:
            inicio = horarios_data.get(f'{dia}_inicio')
            fin = horarios_data.get(f'{dia}_fin')
            if inicio and fin:
                horarios[dia] = f"{inicio}-{fin}"
            else:
                horarios[dia] = "No disponible"
        else:
            horarios[dia] = "No disponible"
    
    return horarios

def validar_datos_profesional(datos):
    """
    Valida los datos del profesional antes de guardar
    """
    errores = []
    
    # Validar DNI
    dni = datos.get('dni', '').strip()
    if not dni.isdigit() or len(dni) != 8:
        errores.append('El DNI debe tener exactamente 8 dígitos')
    
    # Validar nombres y apellidos
    nombres = datos.get('nombres', '').strip()
    apellidos = datos.get('apellidos', '').strip()
    
    if not nombres or len(nombres) < 2:
        errores.append('Los nombres deben tener al menos 2 caracteres')
    
    if not apellidos or len(apellidos) < 2:
        errores.append('Los apellidos deben tener al menos 2 caracteres')
    
    # Validar email
    email = datos.get('email', '').strip()
    if email:
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            errores.append('Formato de email inválido')
    else:
        errores.append('El email es requerido')
    
    # Validar especialidad
    especialidades_validas = ['CARDIOLOGÍA', 'MEDICINA INTERNA', 'ENDOCRINOLOGÍA', 'PSICOLOGÍA CLÍNICA', 'NEUMOLOGÍA']
    if datos.get('especialidad') not in especialidades_validas:
        errores.append('La especialidad seleccionada no es válida')
    
    # Validar rol
    roles_validos = ['MÉDICO', 'PSICÓLOGO']
    if datos.get('rol') not in roles_validos:
        errores.append('El rol seleccionado no es válido')
    
    return errores