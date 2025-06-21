# controllers/admin_pacientes.py

# from models.admin_pacientes import Paciente, Profesional, Cuidador
from models.actores import db, Paciente, Profesional, Cuidador, PacienteEnfermedadMedico, Enfermedad
from datetime import datetime, date
import re

def obtener_pacientes_con_filtros(estado=None, medico_id=None, fecha_desde=None, fecha_hasta=None, busqueda=None, page=1, per_page=10):
    """
    FUNCIÓN  - Obtiene pacientes aplicando filtros y paginación
    """
    # Convertir fechas si vienen como string
    if fecha_desde:
        fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
    if fecha_hasta:
        fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
    
    # 
    resultado = Paciente.obtener_todos_con_filtros_nuevo(
        estado=estado,
        medico_id=medico_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        busqueda=busqueda,
        page=page,
        per_page=per_page
    )
    
    # Formatear datos para la vista
    pacientes_formateados = []
    for paciente in resultado.items:
        # 
        medicos_asignados = db.session.query(PacienteEnfermedadMedico, Profesional)\
            .join(Profesional, PacienteEnfermedadMedico.medico_id == Profesional.id)\
            .filter(PacienteEnfermedadMedico.paciente_id == paciente.id)\
            .filter(PacienteEnfermedadMedico.estado == 'ACTIVO')\
            .all()
        
        medicos_nombres = []
        if medicos_asignados:
            for asignacion, medico in medicos_asignados:
                medicos_nombres.append(f"Dr. {medico.nombres} {medico.apellidos}")
        
        medico_asignado_str = ", ".join(medicos_nombres) if medicos_nombres else "Sin asignar"
        
        pacientes_formateados.append({
            'id': paciente.id,
            'dni': paciente.dni,
            'nombre_completo': paciente.nombre_completo,
            'edad': f"{paciente.edad} años" if paciente.edad else "No definida",
            'enfermedades': paciente.enfermedades_lista,
            'medico_asignado': medico_asignado_str,  #
            'fecha_registro': paciente.fecha_registro.strftime('%d/%m/%Y'),
            'estado': paciente.estado,
            'tiene_cuidador': paciente.tiene_cuidador
        })
    
    return {
        'pacientes': pacientes_formateados,
        'total': resultado.total,
        'pages': resultado.pages,
        'current_page': resultado.page,
        'per_page': resultado.per_page,
        'has_prev': resultado.has_prev,
        'has_next': resultado.has_next
    }

def obtener_medicos_para_asignacion():
    """
    Obtiene lista de médicos activos para asignación
    """
    medicos = Profesional.obtener_medicos_activos()
    return [{
        'id': medico.id,
        'nombre_formal': medico.nombre_formal, 
        'especialidad': medico.especialidad
    } for medico in medicos]

def crear_nuevo_paciente(datos):
    """
    FUNCIÓN  - Crea un nuevo paciente con los datos proporcionados
    """
    try:
        # Convertir fecha de nacimiento
        fecha_nacimiento = datetime.strptime(datos['fecha_nacimiento'], '%Y-%m-%d').date()
        
        # Convertir enfermedades a lista si viene como string
        enfermedades = datos.get('enfermedades', [])
        if isinstance(enfermedades, str):
            enfermedades = [enfermedades]
        
        # 
        nuevo_paciente = Paciente.crear_paciente_nuevo( 
            dni=datos['dni'],
            nombres=datos['nombres'],
            apellidos=datos['apellidos'],
            fecha_nacimiento=fecha_nacimiento,
            email=datos.get('email'),
            telefono=datos.get('telefono'),  # 
            direccion=datos.get('direccion'),
            enfermedades = datos.get('enfermedades', []),
            medicos_asignados = datos.get('medicos_asignados', {})
        )
        print(nuevo_paciente)
        return {
            'success': True,
            'message': 'Paciente creado exitosamente',
            'paciente_id': nuevo_paciente.id
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al crear paciente: {str(e)}'
        }
    
def obtener_pacientes():
    """
     FUNCIÓN  - Obtiene pacientes con sus médicos asignados
    """
    pacientes = Paciente.obtener_todos_pacientes()
    
    resultado = []
    for p in pacientes:
        # 
        medicos_asignados = db.session.query(PacienteEnfermedadMedico, Profesional)\
            .join(Profesional, PacienteEnfermedadMedico.medico_id == Profesional.id)\
            .filter(PacienteEnfermedadMedico.paciente_id == p.id)\
            .filter(PacienteEnfermedadMedico.estado == 'ACTIVO')\
            .all()
        
        # 
        medicos_nombres = []
        if medicos_asignados:
            for asignacion, medico in medicos_asignados:
                medicos_nombres.append(f"Dr. {medico.nombre_formal}")
        
        resultado.append({
            'id': p.id,
            'nombre_completo': p.nombre_completo,
            'edad': p.edad,
            'dni': p.dni,
            'enfermedades': p.enfermedades_lista,
            'medico_asignado': medicos_nombres,  # 
            'estado': p.estado
        })

    return resultado

    
    

def obtener_paciente_por_id(paciente_id):
    """
    FUNCIÓN  - Obtiene datos completos de un paciente específico
    """
    paciente = Paciente.query.get(paciente_id)
    if not paciente:
        return None
    
    # NUEVO: Obtener médicos asignados con enfermedades
    asignaciones_medicas = db.session.query(PacienteEnfermedadMedico, Profesional, Enfermedad)\
        .join(Profesional, PacienteEnfermedadMedico.medico_id == Profesional.id)\
        .join(Enfermedad, PacienteEnfermedadMedico.enfermedad_id == Enfermedad.id)\
        .filter(PacienteEnfermedadMedico.paciente_id == paciente_id)\
        .filter(PacienteEnfermedadMedico.estado == 'ACTIVO')\
        .all()
    
    # FORMATEAR: Médicos asignados por enfermedad
    medicos_asignados = []
    for asignacion, medico, enfermedad in asignaciones_medicas:
        medicos_asignados.append({
            'id': medico.id,
            'nombre': f"Dr. {medico.nombres} {medico.apellidos}",
            'especialidad': medico.especialidad,
            'enfermedad': enfermedad.nombre,
            'observaciones': asignacion.observaciones
        })
    
    return {
        'id': paciente.id,
        'dni': paciente.dni,
        'nombres': paciente.nombres,
        'apellidos': paciente.apellidos,
        'nombre_completo': paciente.nombre_completo,
        'fecha_nacimiento': paciente.fecha_nacimiento.strftime('%Y-%m-%d'),
        'edad': paciente.edad,
        'email': paciente.email,
        'telefono': paciente.telefono,
        'direccion': paciente.direccion,
        'enfermedades': paciente.enfermedades_lista,
        'estado': paciente.estado,
        'fecha_registro': paciente.fecha_registro.strftime('%d/%m/%Y %H:%M'),
        'medicos_asignados': medicos_asignados,  # 
        'cuidadores': [{
            'id': cuidador.id,
            'nombre_completo': cuidador.nombre_completo,
            'dni': cuidador.dni,
            'telefono': cuidador.telefono,
            'relacion': cuidador.relacion_paciente,
            'estado': cuidador.estado
        } for cuidador in paciente.cuidadores]
    }

# def actualizar_paciente(paciente_id, datos):
def actualizar_paciente(paciente_id, datos, medico_id=None):
    """
    FUNCIÓN: Actualiza los datos de un paciente existente
    """
    try:
        paciente = Paciente.query.get(paciente_id)
        if not paciente:
            return {'success': False, 'message': 'Paciente no encontrado'}
        
        # Actualizar campos básicos del paciente
        paciente.nombres = datos.get('nombres', paciente.nombres)
        paciente.apellidos = datos.get('apellidos', paciente.apellidos)
        paciente.email = datos.get('email', paciente.email)
        paciente.telefono = datos.get('telefono', paciente.telefono)
        paciente.direccion = datos.get('direccion', paciente.direccion)
        
        if 'fecha_nacimiento' in datos:
            paciente.fecha_nacimiento = datetime.strptime(datos['fecha_nacimiento'], '%Y-%m-%d').date()
        
        # Actualizar enfermedades y tabla de relación
        if 'enfermedades' in datos and medico_id:
            enfermedades = datos['enfermedades']
            if isinstance(enfermedades, str):
                enfermedades = [enfermedades]
            
            # 1. ELIMINAR asignaciones existentes para este paciente y médico
            PacienteEnfermedadMedico.query.filter_by(
                paciente_id=paciente_id,
                medico_id=medico_id
            ).delete()
            
            # 2. INSERTAR nuevas asignaciones
            for enfermedad_id in enfermedades:
                nueva_asignacion = PacienteEnfermedadMedico(
                    paciente_id=paciente_id,
                    enfermedad_id=enfermedad_id,
                    medico_id=medico_id,
                    estado='ACTIVO',
                    observaciones=datos.get('observaciones', None)
                )
                db.session.add(nueva_asignacion)
            
            # Actualizar el campo enfermedades del paciente (si lo tienes)
            paciente.enfermedades = enfermedades
        
        # Confirmar todos los cambios
        db.session.commit()
        
        return {'success': True, 'message': 'Paciente actualizado exitosamente'}
        
    except Exception as e:
        db.session.rollback()  # Revertir cambios en caso de error
        return {'success': False, 'message': f'Error al actualizar paciente: {str(e)}'}



def cambiar_estado_paciente(paciente_id):
    """
    Cambia el estado de un paciente entre ACTIVO/INACTIVO
    """
    try:
        paciente = Paciente.query.get(paciente_id)
        if not paciente:
            return {'success': False, 'message': 'Paciente no encontrado'}
        
        nuevo_estado = paciente.actualizar_estado()
        
        return {
            'success': True,
            'message': f'Estado del paciente cambiado a {nuevo_estado}',
            'nuevo_estado': nuevo_estado
        }
    except Exception as e:
        return {'success': False, 'message': f'Error al cambiar estado: {str(e)}'}

def asignar_cuidador_a_paciente(paciente_id, datos_cuidador):
    """
    Asigna un cuidador a un paciente
    """
    try:
        # Verificar que el paciente existe
        paciente = Paciente.query.get(paciente_id)
        if not paciente:
            return {'success': False, 'message': 'Paciente no encontrado'}
        
        # Crear el cuidador
        cuidador = Cuidador.crear_cuidador(
            paciente_id=paciente_id,
            nombre_completo=datos_cuidador['nombre_completo'],
            dni=datos_cuidador['dni'],
            telefono=datos_cuidador['telefono'],
            relacion_paciente=datos_cuidador['relacion_paciente']
        )
        
        return {
            'success': True,
            'message': f'Cuidador {cuidador.nombre_completo} asignado exitosamente',
            'cuidador_id': cuidador.id
        }
    except Exception as e:
        return {'success': False, 'message': f'Error al asignar cuidador: {str(e)}'}
    


def actualizar_paciente_completo(data):
    """
    Actualiza datos completos de un paciente y sus cuidadores
    """
    try:
        # Validar que se recibieron datos
        if not data:
            return {'success': False, 'message': 'No se recibieron datos'}
        
        # Validar campos requeridos
        campos_requeridos = ['paciente_id', 'nombres', 'apellidos', 'dni', 'fecha_nacimiento']
        for campo in campos_requeridos:
            if not data.get(campo):
                return {'success': False, 'message': f'El campo {campo} es requerido'}
        
        # Obtener el paciente
        paciente_id = data.get('paciente_id')
        paciente = Paciente.query.get(paciente_id)
        
        if not paciente:
            return {'success': False, 'message': 'Paciente no encontrado'}
        
        # Validar que el DNI no esté en uso por otro paciente
        dni_existente = Paciente.query.filter(
            Paciente.dni == data.get('dni'),
            Paciente.id != paciente_id
        ).first()
        
        if dni_existente:
            return {'success': False, 'message': 'El DNI ya está registrado por otro paciente'}
        
        # Validar datos antes de actualizar
        errores_validacion = validar_datos_paciente_completo(data)
        if errores_validacion:
            return {'success': False, 'message': '; '.join(errores_validacion)}
        
        # Actualizar datos básicos del paciente
        paciente.nombres = data.get('nombres').strip()
        paciente.apellidos = data.get('apellidos').strip()
        paciente.dni = data.get('dni').strip()
        paciente.fecha_nacimiento = datetime.strptime(data.get('fecha_nacimiento'), '%Y-%m-%d').date()
        paciente.email = data.get('email', '').strip() if data.get('email') else None
        paciente.telefono = data.get('telefono', '').strip() if data.get('telefono') else None
        paciente.direccion = data.get('direccion', '').strip() if data.get('direccion') else None
        
        # Actualizar enfermedades
        enfermedades = data.get('enfermedades', [])
        if enfermedades:
            paciente.enfermedades = ','.join(enfermedades)
        else:
            paciente.enfermedades = None
        
        # ===============================
        # GESTIÓN DE CUIDADORES
        # ===============================
        
        # 1. Eliminar cuidadores marcados para eliminación
        cuidadores_eliminados = data.get('cuidadores_eliminados', [])
        for cuidador_id in cuidadores_eliminados:
            if cuidador_id.isdigit():  # Solo IDs numéricos (cuidadores existentes)
                cuidador = Cuidador.query.get(int(cuidador_id))
                if cuidador and cuidador.paciente_id == paciente.id:
                    db.session.delete(cuidador)
                    print(f"Cuidador {cuidador_id} eliminado")
        
        # 2. Actualizar cuidadores existentes
        cuidadores_actualizados = data.get('cuidadores', [])
        for cuidador_data in cuidadores_actualizados:
            cuidador_id = cuidador_data.get('id')
            if cuidador_id and cuidador_id.isdigit():
                cuidador = Cuidador.query.get(int(cuidador_id))
                if cuidador and cuidador.paciente_id == paciente.id:
                    # Validar DNI único entre cuidadores
                    dni_cuidador_existente = Cuidador.query.filter(
                        Cuidador.dni == cuidador_data.get('dni'),
                        Cuidador.id != cuidador.id,
                        Cuidador.paciente_id == paciente.id
                    ).first()
                    
                    if dni_cuidador_existente:
                        return {
                            'success': False, 
                            'message': f'El DNI {cuidador_data.get("dni")} ya existe en otro cuidador'
                        }
                    
                    # Validar datos del cuidador
                    errores_cuidador = validar_datos_cuidador(cuidador_data)
                    if errores_cuidador:
                        return {'success': False, 'message': '; '.join(errores_cuidador)}
                    
                    # Actualizar datos
                    cuidador.nombre_completo = cuidador_data.get('nombre', '').strip()
                    cuidador.dni = cuidador_data.get('dni', '').strip()
                    cuidador.telefono = cuidador_data.get('telefono', '').strip()
                    cuidador.relacion_paciente = cuidador_data.get('relacion', '')
                    cuidador.estado = cuidador_data.get('estado', 'activo')
                    print(f"Cuidador {cuidador_id} actualizado")
        
        # 3. Crear nuevos cuidadores
        cuidadores_nuevos = data.get('cuidadores_nuevos', [])
        for cuidador_data in cuidadores_nuevos:
            # Validar DNI único
            dni_cuidador_existente = Cuidador.query.filter(
                Cuidador.dni == cuidador_data.get('dni'),
                Cuidador.paciente_id == paciente.id
            ).first()
            
            if dni_cuidador_existente:
                return {
                    'success': False, 
                    'message': f'El DNI {cuidador_data.get("dni")} ya existe en otro cuidador'
                }
            
            # Validar datos del cuidador
            errores_cuidador = validar_datos_cuidador(cuidador_data)
            if errores_cuidador:
                return {'success': False, 'message': '; '.join(errores_cuidador)}
            
            # Crear nuevo cuidador
            nuevo_cuidador = Cuidador(
                paciente_id=paciente.id,
                nombre_completo=cuidador_data.get('nombre', '').strip(),
                dni=cuidador_data.get('dni', '').strip(),
                telefono=cuidador_data.get('telefono', '').strip(),
                relacion_paciente=cuidador_data.get('relacion', ''),
                estado=cuidador_data.get('estado', 'activo')
            )
            
            db.session.add(nuevo_cuidador)
            print(f"Nuevo cuidador creado: {nuevo_cuidador.nombre_completo}")
        
        # Guardar todos los cambios
        db.session.commit()
        
        return {
            'success': True, 
            'message': 'Paciente y cuidadores actualizados exitosamente',
            'paciente': {
                'id': paciente.id,
                'nombre_completo': paciente.nombre_completo,
                'dni': paciente.dni,
                'email': paciente.email,
                'estado': paciente.estado
            }
        }
        
    except ValueError as e:
        db.session.rollback()
        return {'success': False, 'message': 'Formato de fecha inválido'}
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar paciente: {e}")
        return {'success': False, 'message': 'Error interno del servidor'}


def validar_datos_paciente_completo(data):
    """
    Valida los datos completos del paciente antes de guardar
    """
    errores = []
    
    # Validar DNI
    dni = data.get('dni', '').strip()
    if not dni.isdigit() or len(dni) != 8:
        errores.append('El DNI debe tener exactamente 8 dígitos')
    
    # Validar nombres y apellidos
    nombres = data.get('nombres', '').strip()
    apellidos = data.get('apellidos', '').strip()
    
    if not nombres or len(nombres) < 2:
        errores.append('Los nombres deben tener al menos 2 caracteres')
    
    if not apellidos or len(apellidos) < 2:
        errores.append('Los apellidos deben tener al menos 2 caracteres')
    
    # Validar fecha de nacimiento
    try:
        fecha_nacimiento = datetime.strptime(data.get('fecha_nacimiento'), '%Y-%m-%d').date()
        if fecha_nacimiento > date.today():
            errores.append('La fecha de nacimiento no puede ser una fecha futura')
    except (ValueError, TypeError):
        errores.append('Formato de fecha inválido')
    
    # Validar email si se proporciona
    email = data.get('email', '').strip()
    if email:
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            errores.append('Formato de email inválido')
    
    return errores


def validar_datos_cuidador(data):
    """
    Valida los datos del cuidador antes de guardar
    """
    errores = []
    
    # Validar DNI
    dni = data.get('dni', '').strip()
    if not dni.isdigit() or len(dni) != 8:
        errores.append('El DNI del cuidador debe tener exactamente 8 dígitos')
    
    # Validar nombre
    nombre = data.get('nombre', '').strip()
    if not nombre or len(nombre) < 2:
        errores.append('El nombre del cuidador debe tener al menos 2 caracteres')
    
    # Validar teléfono
    telefono = data.get('telefono', '').strip()
    if not telefono or len(telefono) < 7:
        errores.append('El teléfono del cuidador debe tener al menos 7 dígitos')
    
    # Validar relación
    relacion = data.get('relacion', '')
    relaciones_validas = ['hijo', 'padre', 'hermano', 'conyuge', 'familiar', 'amistad', 'profesional', 'otro']
    if relacion not in relaciones_validas:
        errores.append('La relación del cuidador no es válida')
    
    return errores