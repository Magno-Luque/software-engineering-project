# controllers/admin_pacientes.py

from models.actores import Paciente, Profesional, Cuidador, PacienteEnfermedadMedico, Enfermedad
from datetime import datetime, date
import json
import re

def obtener_pacientes_con_filtros(estado=None, medico_id=None, fecha_desde=None, fecha_hasta=None, busqueda=None, page=1, per_page=10):
    """
    Obtiene pacientes aplicando filtros y paginación
    """
    try:
        from app import mysql
        
        # Convertir fechas si vienen como string
        if fecha_desde:
            fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        if fecha_hasta:
            fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        
        # Usar el método del modelo con MySQL
        resultado = Paciente.obtener_todos_con_filtros(
            mysql=mysql,
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
        for paciente in resultado['items']:
            # Obtener médicos asignados para este paciente
            asignaciones = PacienteEnfermedadMedico.obtener_asignaciones_paciente(mysql, paciente['id'])
            
            medicos_nombres = []
            for asignacion in asignaciones:
                medicos_nombres.append(f"Dr. {asignacion['medico_nombres']} {asignacion['medico_apellidos']}")
            
            medico_asignado_str = ", ".join(medicos_nombres) if medicos_nombres else "Sin asignar"
            
            # Calcular edad
            edad = Paciente.calcular_edad(paciente['fecha_nacimiento']) if paciente.get('fecha_nacimiento') else None
            
            pacientes_formateados.append({
                'id': paciente['id'],
                'dni': paciente['dni'],
                'nombre_completo': f"{paciente['nombres']} {paciente['apellidos']}",
                'edad': f"{edad} años" if edad else "No definida",
                'enfermedades': paciente.get('enfermedades', []),
                'medico_asignado': medico_asignado_str,
                'fecha_registro': paciente['fecha_registro'].strftime('%d/%m/%Y') if hasattr(paciente['fecha_registro'], 'strftime') else str(paciente['fecha_registro']),
                'estado': paciente['estado'],
                'tiene_cuidador': len(Cuidador.obtener_por_paciente(mysql, paciente['id'])) > 0
            })
        
        return {
            'pacientes': pacientes_formateados,
            'total': resultado['total'],
            'pages': resultado['pages'],
            'current_page': resultado['page'],
            'per_page': resultado['per_page'],
            'has_prev': resultado['page'] > 1,
            'has_next': resultado['page'] < resultado['pages']
        }
        
    except Exception as e:
        print(f"Error en obtener_pacientes_con_filtros: {str(e)}")
        return {
            'pacientes': [],
            'total': 0,
            'pages': 0,
            'current_page': page,
            'per_page': per_page,
            'has_prev': False,
            'has_next': False
        }

def obtener_medicos_para_asignacion():
    """
    Obtiene lista de médicos activos para asignación
    """
    try:
        from app import mysql
        cursor = mysql.connection.cursor()
        
        query = """
            SELECT id, nombres, apellidos, especialidad 
            FROM profesionales 
            WHERE rol = 'MÉDICO' AND estado = 'ACTIVO'
            ORDER BY nombres, apellidos
        """
        cursor.execute(query)
        medicos = cursor.fetchall()
        cursor.close()
        
        # Verificar si es diccionario o tupla y manejar apropiadamente
        resultado = []
        for medico in medicos:
            if isinstance(medico, dict):
                # Si es diccionario (DictCursor configurado)
                resultado.append({
                    'id': medico['id'],
                    'nombre_formal': f"Dr. {medico['nombres']} {medico['apellidos']}",
                    'especialidad': medico['especialidad']
                })
            else:
                # Si es tupla (cursor normal)
                resultado.append({
                    'id': medico[0],  # id
                    'nombre_formal': f"Dr. {medico[1]} {medico[2]}",  # nombres apellidos
                    'especialidad': medico[3]  # especialidad
                })
        
        return resultado
        
    except Exception as e:
        print(f"Error en obtener_medicos_para_asignacion: {str(e)}")
        return []

def crear_nuevo_paciente(datos):
    """
    Crea un nuevo paciente con los datos proporcionados
    """
    try:
        from app import mysql
        
        # Convertir fecha de nacimiento
        fecha_nacimiento = datetime.strptime(datos['fecha_nacimiento'], '%Y-%m-%d').date()
        
        # Convertir enfermedades a lista si viene como string
        enfermedades = datos.get('enfermedades', [])
        if isinstance(enfermedades, str):
            enfermedades = [enfermedades]
        
        # Crear el paciente usando el método del modelo
        paciente_id = Paciente.crear_paciente_nuevo(
            mysql=mysql,
            dni=datos['dni'],
            nombres=datos['nombres'],
            apellidos=datos['apellidos'],
            fecha_nacimiento=fecha_nacimiento,
            email=datos.get('email'),
            telefono=datos.get('telefono'),
            direccion=datos.get('direccion'),
            enfermedades=enfermedades,
            medicos_asignados=datos.get('medicos_asignados', {})
        )
        
        return {
            'success': True,
            'message': 'Paciente creado exitosamente',
            'paciente_id': paciente_id
        }
    except Exception as e:
        print(f"Error en crear_nuevo_paciente: {str(e)}")
        return {
            'success': False,
            'message': f'Error al crear paciente: {str(e)}'
        }

def obtener_pacientes():
    """
    Obtiene pacientes con sus médicos asignados
    """
    try:
        from app import mysql
        pacientes = Paciente.obtener_todos_pacientes(mysql)
        
        resultado = []
        for p in pacientes:
            # Obtener médicos asignados para este paciente
            asignaciones = PacienteEnfermedadMedico.obtener_asignaciones_paciente(mysql, p['id'])
            
            medicos_nombres = []
            for asignacion in asignaciones:
                medicos_nombres.append(f"Dr. {asignacion['medico_nombres']} {asignacion['medico_apellidos']}")
            
            # Calcular edad
            edad = Paciente.calcular_edad(p['fecha_nacimiento']) if p.get('fecha_nacimiento') else None
            
            # Procesar enfermedades - convertir de JSON a lista si es necesario
            enfermedades_lista = []
            if p.get('enfermedades'):
                if isinstance(p['enfermedades'], str):
                    # Si es string JSON, convertir a lista
                    import json
                    try:
                        enfermedades_lista = json.loads(p['enfermedades'])
                    except:
                        enfermedades_lista = [p['enfermedades']]
                elif isinstance(p['enfermedades'], list):
                    enfermedades_lista = p['enfermedades']
                else:
                    enfermedades_lista = []
            
            resultado.append({
                'id': p['id'],
                'nombre_completo': f"{p['nombres']} {p['apellidos']}",
                'edad': edad,
                'dni': p['dni'],
                'enfermedades': enfermedades_lista,  # Asegurar que sea una lista
                'medico_asignado': medicos_nombres,
                'estado': p['estado']
            })

        return resultado
        
    except Exception as e:
        print(f"Error en obtener_pacientes: {str(e)}")
        return []

def obtener_paciente_por_id(paciente_id):
    """
    Obtiene datos completos de un paciente específico
    """
    try:
        from app import mysql
        
        paciente = Paciente.obtener_por_id(mysql, paciente_id)
        if not paciente:
            return None
        
        # Obtener asignaciones médicas
        asignaciones_medicas = PacienteEnfermedadMedico.obtener_asignaciones_paciente(mysql, paciente_id)
        
        # Formatear médicos asignados por enfermedad
        medicos_asignados = []
        for asignacion in asignaciones_medicas:
            medicos_asignados.append({
                'id': asignacion['medico_id'],
                'nombre': f"Dr. {asignacion['medico_nombres']} {asignacion['medico_apellidos']}",
                'especialidad': asignacion['especialidad'],
                'enfermedad': asignacion['enfermedad_nombre'],
                'observaciones': asignacion.get('observaciones', '')
            })
        
        # Obtener cuidadores
        cuidadores = Cuidador.obtener_por_paciente(mysql, paciente_id)
        
        # Calcular edad
        edad = Paciente.calcular_edad(paciente['fecha_nacimiento']) if paciente.get('fecha_nacimiento') else None
        
        # Parsear enfermedades si es un string JSON
        enfermedades_raw = paciente.get('enfermedades', [])
        enfermedades = []
        
        if enfermedades_raw:
            if isinstance(enfermedades_raw, str):
                try:
                    enfermedades = json.loads(enfermedades_raw)
                except json.JSONDecodeError:
                    print(f"Error al parsear enfermedades JSON: {enfermedades_raw}")
                    enfermedades = []
            elif isinstance(enfermedades_raw, list):
                enfermedades = enfermedades_raw
            else:
                enfermedades = []
        
        return {
            'id': paciente['id'],
            'dni': paciente['dni'],
            'nombres': paciente['nombres'],
            'apellidos': paciente['apellidos'],
            'nombre_completo': f"{paciente['nombres']} {paciente['apellidos']}",
            'fecha_nacimiento': paciente['fecha_nacimiento'].strftime('%Y-%m-%d') if hasattr(paciente['fecha_nacimiento'], 'strftime') else str(paciente['fecha_nacimiento']),
            'edad': edad,
            'email': paciente.get('email', ''),
            'telefono': paciente.get('telefono', ''),
            'direccion': paciente.get('direccion', ''),
            'enfermedades': enfermedades,  
            'estado': paciente['estado'],
            'fecha_registro': paciente['fecha_registro'].strftime('%d/%m/%Y %H:%M') if hasattr(paciente['fecha_registro'], 'strftime') else str(paciente['fecha_registro']),
            'medicos_asignados': medicos_asignados,
            'cuidadores': [{
                'id': cuidador['id'],
                'nombre_completo': cuidador['nombre_completo'],
                'dni': cuidador['dni'],
                'telefono': cuidador['telefono'],
                'relacion': cuidador['relacion_paciente'],
                'estado': cuidador['estado']
            } for cuidador in cuidadores]
        }
        
    except Exception as e:
        print(f"Error en obtener_paciente_por_id: {str(e)}")
        return None

def actualizar_paciente(paciente_id, datos):
    """
    Actualiza los datos de un paciente existente con validaciones
    """
    try:
        from app import mysql
        cursor = mysql.connection.cursor()
        
        # 1. Verificar que el paciente existe
        cursor.execute("SELECT * FROM pacientes WHERE id = %s", (paciente_id,))
        paciente_actual = cursor.fetchone()
        
        if not paciente_actual:
            cursor.close()
            return {'success': False, 'message': 'Paciente no encontrado'}
        
        # 2. Validaciones básicas
        errores = []
        
        # Validar DNI duplicado
        dni = datos.get('dni', '').strip()
        if dni and dni != paciente_actual['dni']:
            cursor.execute("SELECT id FROM pacientes WHERE dni = %s AND id != %s", (dni, paciente_id))
            if cursor.fetchone():
                errores.append('Este DNI ya está registrado para otro paciente')
        
        # Validar email duplicado
        email = datos.get('email', '').strip()
        if email:
            cursor.execute("SELECT id FROM pacientes WHERE email = %s AND id != %s", (email, paciente_id))
            if cursor.fetchone():
                errores.append('Este email ya está registrado para otro paciente')
        
        # Validar teléfono duplicado
        telefono = datos.get('telefono', '').strip()
        if telefono:
            cursor.execute("SELECT id FROM pacientes WHERE telefono = %s AND id != %s", (telefono, paciente_id))
            if cursor.fetchone():
                errores.append('Este teléfono ya está registrado para otro paciente')
        
        # Validar DNI del cuidador si existe
        cuidador_dni = datos.get('cuidador_dni', '').strip()
        if cuidador_dni:
            # No puede ser igual al DNI del paciente
            if cuidador_dni == dni:
                errores.append('El DNI del cuidador no puede ser igual al del paciente')
            else:
                # No puede estar duplicado
                cuidador_id = datos.get('cuidador_id')
                if cuidador_id and cuidador_id != 'nuevo':
                    cursor.execute("SELECT id FROM cuidadores WHERE dni = %s AND id != %s", (cuidador_dni, cuidador_id))
                else:
                    cursor.execute("SELECT id FROM cuidadores WHERE dni = %s", (cuidador_dni,))
                
                if cursor.fetchone():
                    errores.append('Este DNI del cuidador ya está registrado')
        
        # Si hay errores, retornar
        if errores:
            cursor.close()
            return {
                'success': False, 
                'message': 'Errores de validación encontrados',
                'errores': errores
            }
        
        # 3. Actualizar datos del paciente
        query = """
            UPDATE pacientes 
            SET nombres = %s, apellidos = %s, email = %s, telefono = %s, direccion = %s
        """
        params = [
            datos.get('nombres', paciente_actual['nombres']).strip(),
            datos.get('apellidos', paciente_actual['apellidos']).strip(),
            email or None,
            telefono or None,
            datos.get('direccion', paciente_actual.get('direccion', '')).strip() or None
        ]
        
        # Actualizar fecha de nacimiento si viene
        if 'fecha_nacimiento' in datos and datos['fecha_nacimiento']:
            query += ", fecha_nacimiento = %s"
            fecha_nacimiento = datetime.strptime(datos['fecha_nacimiento'], '%Y-%m-%d').date()
            params.append(fecha_nacimiento)
        
        # Actualizar DNI si cambió
        if dni and dni != paciente_actual['dni']:
            query += ", dni = %s"
            params.append(dni)
        
        query += " WHERE id = %s"
        params.append(paciente_id)
        
        cursor.execute(query, params)
        
        # 4. Actualizar asignaciones médicas si vienen
        if 'enfermedades' in datos and 'medicos_asignados' in datos:
            # Eliminar asignaciones existentes
            cursor.execute("DELETE FROM paciente_enfermedad_medico WHERE paciente_id = %s", (paciente_id,))
            
            # Insertar nuevas asignaciones
            enfermedad_nombre_a_id = {"diabetes": 1, "hipertension": 2, "asma": 3, "cardiovascular": 4}
            enfermedades = datos['enfermedades']
            medicos_asignados = datos['medicos_asignados']
            
            if "medicina_interna" in medicos_asignados:
                # Medicina interna para todas
                medico_medicina_interna_id = medicos_asignados["medicina_interna"]
                for enfermedad_nombre in enfermedades:
                    enfermedad_id = enfermedad_nombre_a_id.get(enfermedad_nombre)
                    if enfermedad_id:
                        cursor.execute("""
                            INSERT INTO paciente_enfermedad_medico (paciente_id, enfermedad_id, medico_id, estado)
                            VALUES (%s, %s, %s, %s)
                        """, (paciente_id, enfermedad_id, medico_medicina_interna_id, 'ACTIVO'))
            else:
                # Médicos específicos por enfermedad
                for enfermedad_nombre in enfermedades:
                    enfermedad_id = enfermedad_nombre_a_id.get(enfermedad_nombre)
                    medico_id = medicos_asignados.get(enfermedad_nombre)
                    if enfermedad_id and medico_id:
                        cursor.execute("""
                            INSERT INTO paciente_enfermedad_medico (paciente_id, enfermedad_id, medico_id, estado)
                            VALUES (%s, %s, %s, %s)
                        """, (paciente_id, enfermedad_id, medico_id, 'ACTIVO'))
            
            # Actualizar campo enfermedades
            import json
            cursor.execute("UPDATE pacientes SET enfermedades = %s WHERE id = %s", 
                         (json.dumps(enfermedades), paciente_id))
        
        # 5. Manejar cuidador
        if datos.get('eliminar_cuidador') == 'true':
            cursor.execute("DELETE FROM cuidadores WHERE paciente_id = %s", (paciente_id,))
        elif 'cuidador_nombre' in datos and datos['cuidador_nombre'].strip():
            cuidador_id = datos.get('cuidador_id')
            nombre = datos.get('cuidador_nombre').strip()
            dni_cuidador = datos.get('cuidador_dni').strip()
            telefono_cuidador = datos.get('cuidador_telefono').strip()
            relacion = datos.get('cuidador_relacion')
            
            if cuidador_id == 'nuevo':
                # Crear nuevo cuidador
                cursor.execute("""
                    INSERT INTO cuidadores (paciente_id, nombre_completo, dni, telefono, relacion_paciente, estado)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (paciente_id, nombre, dni_cuidador, telefono_cuidador, relacion, 'ACTIVO'))
            else:
                # Actualizar cuidador existente
                cursor.execute("""
                    UPDATE cuidadores 
                    SET nombre_completo = %s, dni = %s, telefono = %s, relacion_paciente = %s
                    WHERE id = %s AND paciente_id = %s
                """, (nombre, dni_cuidador, telefono_cuidador, relacion, cuidador_id, paciente_id))
        
        mysql.connection.commit()
        cursor.close()
        
        return {'success': True, 'message': 'Paciente actualizado exitosamente'}
        
    except Exception as e:
        mysql.connection.rollback()
        if 'cursor' in locals():
            cursor.close()
        print(f"Error en actualizar_paciente: {str(e)}")
        return {'success': False, 'message': f'Error interno del servidor'}

def cambiar_estado_paciente(paciente_id):
    """
    Cambia el estado de un paciente entre ACTIVO/INACTIVO
    """
    try:
        from app import mysql
        
        nuevo_estado = Paciente.actualizar_estado(mysql, paciente_id)
        if nuevo_estado:
            return {
                'success': True,
                'message': f'Estado del paciente cambiado a {nuevo_estado}',
                'nuevo_estado': nuevo_estado
            }
        else:
            return {'success': False, 'message': 'Paciente no encontrado'}
            
    except Exception as e:
        print(f"Error en cambiar_estado_paciente: {str(e)}")
        return {'success': False, 'message': f'Error al cambiar estado: {str(e)}'}

def asignar_cuidador_a_paciente(paciente_id, datos_cuidador):
    """
    Asigna un cuidador a un paciente
    """
    try:
        from app import mysql
        
        # Verificar que el paciente existe
        paciente = Paciente.obtener_por_id(mysql, paciente_id)
        if not paciente:
            return {'success': False, 'message': 'Paciente no encontrado'}
        
        # Crear el cuidador
        cuidador_id = Cuidador.crear_cuidador(
            mysql=mysql,
            paciente_id=paciente_id,
            nombre_completo=datos_cuidador['nombre_completo'],
            dni=datos_cuidador['dni'],
            telefono=datos_cuidador['telefono'],
            relacion_paciente=datos_cuidador['relacion_paciente']
        )
        
        return {
            'success': True,
            'message': f'Cuidador {datos_cuidador["nombre_completo"]} asignado exitosamente',
            'cuidador_id': cuidador_id
        }
    except Exception as e:
        print(f"Error en asignar_cuidador_a_paciente: {str(e)}")
        return {'success': False, 'message': f'Error al asignar cuidador: {str(e)}'}

def actualizar_paciente_completo(data):
    """
    Actualiza datos completos de un paciente y sus cuidadores
    """
    try:
        from app import mysql
        
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
        paciente = Paciente.obtener_por_id(mysql, paciente_id)
        
        if not paciente:
            return {'success': False, 'message': 'Paciente no encontrado'}
        
        # Validar datos antes de actualizar
        errores_validacion = validar_datos_paciente_completo(data)
        if errores_validacion:
            return {'success': False, 'message': '; '.join(errores_validacion)}
        
        cursor = mysql.connection.cursor()
        
        # Actualizar datos básicos del paciente
        query_paciente = """
            UPDATE pacientes 
            SET nombres = %s, apellidos = %s, dni = %s, fecha_nacimiento = %s,
                email = %s, telefono = %s, direccion = %s
            WHERE id = %s
        """
        
        fecha_nacimiento = datetime.strptime(data.get('fecha_nacimiento'), '%Y-%m-%d').date()
        
        cursor.execute(query_paciente, (
            data.get('nombres').strip(),
            data.get('apellidos').strip(),
            data.get('dni').strip(),
            fecha_nacimiento,
            data.get('email', '').strip() if data.get('email') else None,
            data.get('telefono', '').strip() if data.get('telefono') else None,
            data.get('direccion', '').strip() if data.get('direccion') else None,
            paciente_id
        ))
        
        # Gestión de cuidadores existentes
        cuidadores_actualizados = data.get('cuidadores', [])
        for cuidador_data in cuidadores_actualizados:
            cuidador_id = cuidador_data.get('id')
            if cuidador_id and str(cuidador_id).isdigit():
                # Validar datos del cuidador
                errores_cuidador = validar_datos_cuidador(cuidador_data)
                if errores_cuidador:
                    mysql.connection.rollback()
                    return {'success': False, 'message': '; '.join(errores_cuidador)}
                
                # Actualizar cuidador existente
                query_cuidador = """
                    UPDATE cuidadores 
                    SET nombre_completo = %s, dni = %s, telefono = %s, relacion_paciente = %s
                    WHERE id = %s AND paciente_id = %s
                """
                cursor.execute(query_cuidador, (
                    cuidador_data.get('nombre', '').strip(),
                    cuidador_data.get('dni', '').strip(),
                    cuidador_data.get('telefono', '').strip(),
                    cuidador_data.get('relacion', ''),
                    cuidador_id,
                    paciente_id
                ))
        
        # Crear nuevos cuidadores
        cuidadores_nuevos = data.get('cuidadores_nuevos', [])
        for cuidador_data in cuidadores_nuevos:
            # Validar datos del cuidador
            errores_cuidador = validar_datos_cuidador(cuidador_data)
            if errores_cuidador:
                mysql.connection.rollback()
                return {'success': False, 'message': '; '.join(errores_cuidador)}
            
            # Crear nuevo cuidador
            query_nuevo_cuidador = """
                INSERT INTO cuidadores (paciente_id, nombre_completo, dni, telefono, relacion_paciente, estado)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_nuevo_cuidador, (
                paciente_id,
                cuidador_data.get('nombre', '').strip(),
                cuidador_data.get('dni', '').strip(),
                cuidador_data.get('telefono', '').strip(),
                cuidador_data.get('relacion', ''),
                'ACTIVO'
            ))
        
        # Eliminar cuidadores marcados para eliminación
        cuidadores_eliminados = data.get('cuidadores_eliminados', [])
        for cuidador_id in cuidadores_eliminados:
            if str(cuidador_id).isdigit():
                cursor.execute("""
                    DELETE FROM cuidadores 
                    WHERE id = %s AND paciente_id = %s
                """, (cuidador_id, paciente_id))
        
        mysql.connection.commit()
        cursor.close()
        
        # Obtener datos actualizados del paciente
        paciente_actualizado = Paciente.obtener_por_id(mysql, paciente_id)
        
        return {
            'success': True, 
            'message': 'Paciente y cuidadores actualizados exitosamente',
            'paciente': {
                'id': paciente_actualizado['id'],
                'nombre_completo': f"{paciente_actualizado['nombres']} {paciente_actualizado['apellidos']}",
                'dni': paciente_actualizado['dni'],
                'email': paciente_actualizado.get('email', ''),
                'estado': paciente_actualizado['estado']
            }
        }
        
    except ValueError as e:
        mysql.connection.rollback()
        return {'success': False, 'message': 'Formato de fecha inválido'}
    except Exception as e:
        mysql.connection.rollback()
        print(f"Error al actualizar paciente completo: {e}")
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
    relaciones_validas = ['hijo', 'padre', 'hermano', 'conyugue', 'familiar', 'amigo', 'profesional', 'otro']
    if relacion not in relaciones_validas:
        errores.append('La relación del cuidador no es válida')
    
    return errores