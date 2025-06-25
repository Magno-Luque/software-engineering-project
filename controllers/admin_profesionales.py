# controllers/admin_profesionales.py

from models.actores import Paciente, Profesional, Cuidador, PacienteEnfermedadMedico, Enfermedad
from datetime import datetime, date
import re
import json

def obtener_profesionales():
    """
    Obtiene todos los profesionales con datos básicos para la vista principal
    """
    try:
        from app import mysql
        
        profesionales = Profesional.obtener_todos_activos(mysql)
        
        resultado = []
        for prof in profesionales:
            # Contar pacientes asignados desde la tabla intermedia
            cursor = mysql.connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count FROM paciente_enfermedad_medico 
                WHERE medico_id = %s AND estado = 'ACTIVO'
            """, (prof['id'],))
            pacientes_count = cursor.fetchone()['count']
            cursor.close()
            
            # Formatear horarios
            horario_formateado = formatear_horario_atencion(prof.get('horario_atencion'))
            
            resultado.append({
                'id': prof['id'],
                'nombre_completo': f"{prof['nombres']} {prof['apellidos']}",
                'dni': prof['dni'],
                'especialidad': prof['especialidad'],
                'rol': prof['rol'],
                'horario_atencion': horario_formateado,
                'pacientes_asignados': pacientes_count,
                'email': prof.get('email', ''),
                'telefono': prof.get('telefono', ''),
                'estado': prof['estado'],
                'fecha_registro': prof['fecha_registro'].strftime('%d/%m/%Y') if hasattr(prof['fecha_registro'], 'strftime') else 'No registrada'
            })
        
        return resultado
        
    except Exception as e:
        print(f"Error en obtener_profesionales: {str(e)}")
        return []

def obtener_profesionales_con_filtros(especialidad=None, rol=None, estado=None, busqueda=None, page=1, per_page=10):
    """
    Obtiene profesionales aplicando filtros y paginación
    """
    try:
        from app import mysql
        cursor = mysql.connection.cursor()
        
        # Construir query base
        query = """
            SELECT * FROM profesionales 
            WHERE 1=1
        """
        params = []
        
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
                query += " AND especialidad = %s"
                params.append(especialidad_map[especialidad])
        
        # Filtro por rol
        if rol and rol != 'todos':
            rol_map = {
                'medico': 'MÉDICO',
                'psicologo': 'PSICÓLOGO'
            }
            if rol in rol_map:
                query += " AND rol = %s"
                params.append(rol_map[rol])
        
        # Filtro por estado
        if estado and estado != 'todos':
            query += " AND estado = %s"
            params.append(estado.upper())
        
        # Filtro de búsqueda (nombre o DNI)
        if busqueda:
            query += " AND (nombres LIKE %s OR apellidos LIKE %s OR dni LIKE %s)"
            busqueda_like = f"%{busqueda}%"
            params.extend([busqueda_like, busqueda_like, busqueda_like])
        
        # Contar total de registros
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total = cursor.fetchone()['COUNT(*)']
        
        # Aplicar ordenamiento y paginación
        query += " ORDER BY fecha_registro DESC"
        offset = (page - 1) * per_page
        query += " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        cursor.execute(query, params)
        profesionales = cursor.fetchall()
        
        # Formatear datos para la vista
        profesionales_formateados = []
        for prof in profesionales:
            # Contar pacientes asignados
            cursor.execute("""
                SELECT COUNT(*) as count FROM paciente_enfermedad_medico 
                WHERE medico_id = %s AND estado = 'ACTIVO'
            """, (prof['id'],))
            pacientes_count = cursor.fetchone()['count']
            
            profesionales_formateados.append({
                'id': prof['id'],
                'nombre_completo': f"{prof['nombres']} {prof['apellidos']}",
                'dni': prof['dni'],
                'especialidad': prof['especialidad'],
                'rol': prof['rol'],
                'horario_atencion': formatear_horario_atencion(prof.get('horario_atencion')),
                'pacientes_asignados': pacientes_count,
                'email': prof.get('email', ''),
                'telefono': prof.get('telefono', ''),
                'estado': prof['estado'],
                'fecha_registro': prof['fecha_registro'].strftime('%d/%m/%Y') if hasattr(prof['fecha_registro'], 'strftime') else 'No registrada'
            })
        
        cursor.close()
        
        return {
            'profesionales': profesionales_formateados,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'current_page': page,
            'per_page': per_page,
            'has_prev': page > 1,
            'has_next': page < ((total + per_page - 1) // per_page)
        }
        
    except Exception as e:
        print(f"Error en obtener_profesionales_con_filtros: {str(e)}")
        return {
            'profesionales': [],
            'total': 0,
            'pages': 0,
            'current_page': page,
            'per_page': per_page,
            'has_prev': False,
            'has_next': False
        }

def obtener_profesional_por_id(profesional_id):
    """
    Obtiene datos completos de un profesional específico
    """
    try:
        from app import mysql
        
        profesional = Profesional.obtener_por_id(mysql, profesional_id)
        if not profesional:
            return None
        
        cursor = mysql.connection.cursor()
        
        # Obtener pacientes asignados con detalles
        query_pacientes = """
            SELECT pem.*, p.nombres as paciente_nombres, p.apellidos as paciente_apellidos, 
                   p.dni as paciente_dni, e.nombre as enfermedad_nombre, pem.fecha_asignacion, pem.observaciones
            FROM paciente_enfermedad_medico pem
            JOIN pacientes p ON pem.paciente_id = p.id
            JOIN enfermedades e ON pem.enfermedad_id = e.id
            WHERE pem.medico_id = %s AND pem.estado = 'ACTIVO'
            ORDER BY pem.fecha_asignacion DESC
        """
        
        cursor.execute(query_pacientes, (profesional_id,))
        pacientes_asignados = cursor.fetchall()
        cursor.close()
        
        # Formatear pacientes asignados
        pacientes_detalle = []
        for asignacion in pacientes_asignados:
            pacientes_detalle.append({
                'id': asignacion['paciente_id'],
                'nombre_completo': f"{asignacion['paciente_nombres']} {asignacion['paciente_apellidos']}",
                'dni': asignacion['paciente_dni'],
                'enfermedad': asignacion['enfermedad_nombre'],
                'fecha_asignacion': asignacion['fecha_asignacion'].strftime('%d/%m/%Y') if hasattr(asignacion['fecha_asignacion'], 'strftime') else str(asignacion['fecha_asignacion']),
                'observaciones': asignacion.get('observaciones', '')
            })
        
        return {
            'id': profesional['id'],
            'dni': profesional['dni'],
            'nombres': profesional['nombres'],
            'apellidos': profesional['apellidos'],
            'nombre_completo': f"{profesional['nombres']} {profesional['apellidos']}",
            'especialidad': profesional['especialidad'],
            'rol': profesional['rol'],
            'telefono': profesional.get('telefono', ''),
            'email': profesional.get('email', ''),
            'horario_atencion': profesional.get('horario_atencion'),
            'pacientes_asignados_count': len(pacientes_detalle),
            'pacientes_asignados': pacientes_detalle,
            'estado': profesional['estado'],
            'fecha_registro': profesional['fecha_registro'].strftime('%d/%m/%Y %H:%M') if hasattr(profesional['fecha_registro'], 'strftime') else 'No registrada'
        }
        
    except Exception as e:
        print(f"Error en obtener_profesional_por_id: {str(e)}")
        return None

def crear_nuevo_profesional(datos):
    """
    Crea un nuevo profesional con los datos proporcionados
    """
    try:
        from app import mysql
        cursor = mysql.connection.cursor()
        
        # Validar que el DNI no exista
        cursor.execute("SELECT id FROM profesionales WHERE dni = %s", (datos['dni'],))
        if cursor.fetchone():
            cursor.close()
            return {
                'success': False,
                'message': 'Ya existe un profesional con este DNI'
            }
        
        # Validar que el email no exista
        cursor.execute("SELECT id FROM profesionales WHERE email = %s", (datos['email'],))
        if cursor.fetchone():
            cursor.close()
            return {
                'success': False,
                'message': 'Ya existe un profesional con este email'
            }
        
        # Procesar horarios de atención
        horarios = procesar_horarios_atencion(datos.get('horarios', {}))
        horarios_json = json.dumps(horarios) if horarios else None
        
        # Crear el profesional
        query = """
            INSERT INTO profesionales 
            (dni, nombres, apellidos, especialidad, rol, telefono, email, horario_atencion, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            datos['dni'],
            datos['nombres'],
            datos['apellidos'],
            datos['especialidad'],
            datos['rol'],
            datos.get('telefono'),
            datos['email'],
            horarios_json,
            'ACTIVO'
        ))
        
        mysql.connection.commit()
        profesional_id = cursor.lastrowid
        cursor.close()
        
        return {
            'success': True,
            'message': 'Profesional creado exitosamente',
            'profesional_id': profesional_id
        }
        
    except Exception as e:
        mysql.connection.rollback()
        print(f"Error en crear_nuevo_profesional: {str(e)}")
        return {
            'success': False,
            'message': f'Error al crear profesional: {str(e)}'
        }

def actualizar_profesional(profesional_id, datos):
    """
    Actualiza los datos de un profesional existente
    """
    try:
        from app import mysql
        cursor = mysql.connection.cursor()
        
        # Verificar que el profesional existe
        cursor.execute("SELECT * FROM profesionales WHERE id = %s", (profesional_id,))
        profesional = cursor.fetchone()
        if not profesional:
            cursor.close()
            return {'success': False, 'message': 'Profesional no encontrado'}
        
        # Validar DNI único (excluyendo el profesional actual)
        cursor.execute("SELECT id FROM profesionales WHERE dni = %s AND id != %s", (datos['dni'], profesional_id))
        if cursor.fetchone():
            cursor.close()
            return {'success': False, 'message': 'El DNI ya está registrado por otro profesional'}
        
        # Validar email único (excluyendo el profesional actual)
        cursor.execute("SELECT id FROM profesionales WHERE email = %s AND id != %s", (datos['email'], profesional_id))
        if cursor.fetchone():
            cursor.close()
            return {'success': False, 'message': 'El email ya está registrado por otro profesional'}
        
        # Procesar horarios si se proporcionan
        horarios_json = None
        if 'horarios' in datos:
            horarios = procesar_horarios_atencion(datos['horarios'])
            horarios_json = json.dumps(horarios) if horarios else None
        
        # Actualizar profesional
        query = """
            UPDATE profesionales 
            SET dni = %s, nombres = %s, apellidos = %s, especialidad = %s, 
                rol = %s, telefono = %s, email = %s
        """
        params = [
            datos.get('dni', profesional['dni']),
            datos.get('nombres', profesional['nombres']),
            datos.get('apellidos', profesional['apellidos']),
            datos.get('especialidad', profesional['especialidad']),
            datos.get('rol', profesional['rol']),
            datos.get('telefono', profesional.get('telefono')),
            datos.get('email', profesional['email'])
        ]
        
        if horarios_json is not None:
            query += ", horario_atencion = %s"
            params.append(horarios_json)
        
        query += " WHERE id = %s"
        params.append(profesional_id)
        
        cursor.execute(query, params)
        mysql.connection.commit()
        cursor.close()
        
        return {'success': True, 'message': 'Profesional actualizado exitosamente'}
        
    except Exception as e:
        mysql.connection.rollback()
        print(f"Error en actualizar_profesional: {str(e)}")
        return {'success': False, 'message': f'Error al actualizar profesional: {str(e)}'}

def cambiar_estado_profesional(profesional_id):
    """
    Cambia el estado de un profesional entre ACTIVO/INACTIVO
    """
    try:
        from app import mysql
        cursor = mysql.connection.cursor()
        
        # Obtener estado actual
        cursor.execute("SELECT estado FROM profesionales WHERE id = %s", (profesional_id,))
        resultado = cursor.fetchone()
        
        if not resultado:
            cursor.close()
            return {'success': False, 'message': 'Profesional no encontrado'}
        
        # Cambiar estado
        nuevo_estado = 'INACTIVO' if resultado['estado'] == 'ACTIVO' else 'ACTIVO'
        cursor.execute("UPDATE profesionales SET estado = %s WHERE id = %s", (nuevo_estado, profesional_id))
        
        mysql.connection.commit()
        cursor.close()
        
        return {
            'success': True,
            'message': f'Estado del profesional cambiado a {nuevo_estado}',
            'nuevo_estado': nuevo_estado
        }
        
    except Exception as e:
        mysql.connection.rollback()
        print(f"Error en cambiar_estado_profesional: {str(e)}")
        return {'success': False, 'message': f'Error al cambiar estado: {str(e)}'}

def obtener_estadisticas_profesionales():
    """
    Obtiene estadísticas generales de profesionales
    """
    try:
        from app import mysql
        cursor = mysql.connection.cursor()
        
        # Total de profesionales
        cursor.execute("SELECT COUNT(*) as total FROM profesionales")
        total_profesionales = cursor.fetchone()['total']
        
        # Profesionales activos
        cursor.execute("SELECT COUNT(*) as activos FROM profesionales WHERE estado = 'ACTIVO'")
        profesionales_activos = cursor.fetchone()['activos']
        
        # Estadísticas por especialidad
        cursor.execute("""
            SELECT especialidad, COUNT(*) as count 
            FROM profesionales 
            GROUP BY especialidad 
            ORDER BY count DESC
        """)
        especialidades = cursor.fetchall()
        
        # Estadísticas por rol
        cursor.execute("""
            SELECT rol, COUNT(*) as count 
            FROM profesionales 
            GROUP BY rol 
            ORDER BY count DESC
        """)
        roles = cursor.fetchall()
        
        cursor.close()
        
        return {
            'total_profesionales': total_profesionales,
            'profesionales_activos': profesionales_activos,
            'profesionales_inactivos': total_profesionales - profesionales_activos,
            'por_especialidad': [{'especialidad': esp['especialidad'], 'count': esp['count']} for esp in especialidades],
            'por_rol': [{'rol': rol['rol'], 'count': rol['count']} for rol in roles]
        }
        
    except Exception as e:
        print(f"Error en obtener_estadisticas_profesionales: {str(e)}")
        return {
            'total_profesionales': 0,
            'profesionales_activos': 0,
            'profesionales_inactivos': 0,
            'por_especialidad': [],
            'por_rol': []
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