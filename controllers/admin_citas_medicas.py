# controllers/admin_citas_medicas.py

from models.cita import Cita
from models.actores import Profesional, Paciente
from datetime import date

def obtener_citas_medicas():
    """
    Obtiene todas las citas médicas para mostrar en la tabla.
    """ 
    try:
        from app import mysql
        citas = Cita.obtener_citas_hoy(mysql)  # O crear un método para obtener todas
        
        # Formatear datos para el frontend
        citas_formateadas = []
        for cita in citas:
            citas_formateadas.append({
                'id': cita['id'],
                'paciente_nombre': f"{cita.get('paciente_nombres', '')} {cita.get('paciente_apellidos', '')}".strip(),
                'paciente_dni': cita.get('paciente_dni', 'N/A'),
                'medico_nombre': f"Dr. {cita.get('medico_nombres', '')} {cita.get('medico_apellidos', '')}".strip(),
                'especialidad': cita['especialidad'],
                'fecha_cita': cita['fecha_cita'].strftime('%d/%m/%Y') if hasattr(cita['fecha_cita'], 'strftime') else str(cita['fecha_cita']),
                'fecha_cita_iso': cita['fecha_cita'].isoformat() if hasattr(cita['fecha_cita'], 'isoformat') else str(cita['fecha_cita']),
                'hora_inicio': cita['hora_inicio'].strftime('%H:%M') if hasattr(cita['hora_inicio'], 'strftime') else str(cita['hora_inicio']),
                'hora_fin': cita['hora_fin'].strftime('%H:%M') if hasattr(cita['hora_fin'], 'strftime') else str(cita['hora_fin']),
                'horario_completo': Cita.formatear_horario_completo(cita['hora_inicio'], cita['hora_fin']),
                'tipo': cita['tipo'],
                'estado': cita['estado'],
                'consultorio': cita['consultorio'] or 'Virtual',
                'enlace_virtual': cita['enlace_virtual'],
                'motivo_consulta': cita['motivo_consulta'] or '',
                'observaciones': cita['observaciones'] or ''
            })
        
        return citas_formateadas
        
    except Exception as e:
        print(f"Error en obtener_citas_medicas: {str(e)}")
        return []

def obtener_citas_con_filtros(fecha=None, medico_id=None, especialidad=None, 
                             estado=None, tipo=None, busqueda=None, 
                             page=1, per_page=10):
    """
    Obtiene citas médicas con filtros aplicados y paginación.
    """
    try:
        from app import mysql
        cursor = mysql.connection.cursor()
        
        # Construir query base
        query = """
            SELECT c.*, 
                   pac.nombres as paciente_nombres, pac.apellidos as paciente_apellidos, pac.dni as paciente_dni,
                   prof.nombres as medico_nombres, prof.apellidos as medico_apellidos,
                   e.nombre as enfermedad_nombre
            FROM citas c
            JOIN pacientes pac ON c.paciente_id = pac.id
            JOIN profesionales prof ON c.medico_id = prof.id
            JOIN enfermedades e ON c.enfermedad_id = e.id
            WHERE 1=1
        """
        
        params = []
        
        # Aplicar filtros
        if fecha and fecha != 'todas':
            query += " AND c.fecha_cita = %s"
            params.append(fecha)
        
        if medico_id and medico_id != 'todos':
            query += " AND c.medico_id = %s"
            params.append(medico_id)
        
        if especialidad and especialidad != 'todas':
            query += " AND c.especialidad = %s"
            params.append(especialidad)
        
        if estado and estado != 'todos':
            query += " AND c.estado = %s"
            params.append(estado)
        
        if tipo and tipo != 'todos':
            query += " AND c.tipo = %s"
            params.append(tipo)
        
        if busqueda:
            query += " AND (pac.nombres LIKE %s OR pac.apellidos LIKE %s OR pac.dni LIKE %s)"
            busqueda_like = f"%{busqueda}%"
            params.extend([busqueda_like, busqueda_like, busqueda_like])
        
        # Contar total de registros - CORREGIDO
        count_query = """
            SELECT COUNT(*) as total
            FROM citas c
            JOIN pacientes pac ON c.paciente_id = pac.id
            JOIN profesionales prof ON c.medico_id = prof.id
            JOIN enfermedades e ON c.enfermedad_id = e.id
            WHERE 1=1
        """
        
        # Aplicar los mismos filtros para el conteo
        count_params = []
        if fecha and fecha != 'todas':
            count_query += " AND c.fecha_cita = %s"
            count_params.append(fecha)
        
        if medico_id and medico_id != 'todos':
            count_query += " AND c.medico_id = %s"
            count_params.append(medico_id)
        
        if especialidad and especialidad != 'todas':
            count_query += " AND c.especialidad = %s"
            count_params.append(especialidad)
        
        if estado and estado != 'todos':
            count_query += " AND c.estado = %s"
            count_params.append(estado)
        
        if tipo and tipo != 'todos':
            count_query += " AND c.tipo = %s"
            count_params.append(tipo)
        
        if busqueda:
            count_query += " AND (pac.nombres LIKE %s OR pac.apellidos LIKE %s OR pac.dni LIKE %s)"
            busqueda_like = f"%{busqueda}%"
            count_params.extend([busqueda_like, busqueda_like, busqueda_like])
        
        # Ejecutar conteo
        cursor.execute(count_query, count_params)
        count_result = cursor.fetchone()
        total = count_result['total'] if count_result else 0
        
        # Aplicar paginación
        query += " ORDER BY c.fecha_cita DESC, c.hora_inicio DESC"
        offset = (page - 1) * per_page
        query += " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        # Ejecutar query principal
        cursor.execute(query, params)
        citas = cursor.fetchall()
        cursor.close()
        
        # Formatear resultados
        citas_formateadas = []
        for cita in citas:
            citas_formateadas.append({
                'id': cita['id'],
                'paciente_nombre': f"{cita['paciente_nombres']} {cita['paciente_apellidos']}",
                'paciente_dni': cita['paciente_dni'],
                'medico_nombre': f"Dr. {cita['medico_nombres']} {cita['medico_apellidos']}",
                'especialidad': cita['especialidad'],
                'fecha_cita': cita['fecha_cita'].strftime('%d/%m/%Y') if hasattr(cita['fecha_cita'], 'strftime') else str(cita['fecha_cita']),
                'fecha_cita_iso': cita['fecha_cita'].isoformat() if hasattr(cita['fecha_cita'], 'isoformat') else str(cita['fecha_cita']),
                'hora_inicio': cita['hora_inicio'].strftime('%H:%M') if hasattr(cita['hora_inicio'], 'strftime') else str(cita['hora_inicio']),
                'hora_fin': cita['hora_fin'].strftime('%H:%M') if hasattr(cita['hora_fin'], 'strftime') else str(cita['hora_fin']),
                'horario_completo': Cita.formatear_horario_completo(cita['hora_inicio'], cita['hora_fin']),
                'tipo': cita['tipo'],
                'estado': cita['estado'],
                'consultorio': cita['consultorio'] or 'Virtual',
                'enlace_virtual': cita['enlace_virtual'],
                'motivo_consulta': cita['motivo_consulta'] or '',
                'observaciones': cita['observaciones'] or '',
                'enfermedad_nombre': cita['enfermedad_nombre']
            })
        
        return {
            'exito': True,
            'citas': citas_formateadas,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page if total > 0 else 1,
                'has_next': page < ((total + per_page - 1) // per_page) if total > 0 else False,
                'has_prev': page > 1
            }
        }
        
    except Exception as e:
        print(f"Error en obtener_citas_con_filtros: {str(e)}")
        import traceback
        traceback.print_exc()  # Para ver el error completo
        return {
            'exito': False,
            'error': f'Error interno: {str(e)}',
            'citas': [],
            'pagination': {
                'page': 1,
                'per_page': per_page,
                'total': 0,
                'pages': 1,
                'has_next': False,
                'has_prev': False
            }
        }

def obtener_medicos_para_filtro():
    """
    Obtiene lista de médicos activos para el filtro.
    """
    try:
        from app import mysql
        medicos = Profesional.obtener_medicos_activos(mysql)
        
        return [{
            'id': medico['id'],
            'nombre_completo': Profesional.obtener_nombre_completo(medico),
            'especialidad': medico['especialidad']
        } for medico in medicos]
        
    except Exception as e:
        print(f"Error en obtener_medicos_para_filtro: {str(e)}")
        return []

def obtener_estadisticas_citas():
    """
    Obtiene estadísticas resumidas de las citas médicas.
    """
    try:
        from app import mysql
        estadisticas = Cita.obtener_estadisticas_citas(mysql)
        
        if not estadisticas:
            return {
                'total_citas': 0,
                'citas_hoy': 0,
                'por_estado': {
                    'agendadas': 0,
                    'atendidas': 0,
                    'canceladas': 0,
                    'no_atendidas': 0
                },
                'por_tipo': {
                    'presenciales': 0,
                    'virtuales': 0
                },
                'por_especialidad': {}
            }
        
        return {
            'total_citas': estadisticas['total_citas'],
            'citas_hoy': len(Cita.obtener_citas_hoy(mysql)),
            'por_estado': {
                'agendadas': estadisticas['agendadas'],
                'atendidas': estadisticas['atendidas'],
                'canceladas': estadisticas['canceladas'],
                'no_atendidas': estadisticas['no_atendidas']
            },
            'por_tipo': {
                'presenciales': estadisticas['total_citas'] - 0,  # Necesitarías agregar este cálculo en el modelo
                'virtuales': 0  # Necesitarías agregar este cálculo en el modelo
            },
            'por_especialidad': {}  # Necesitarías agregar este cálculo en el modelo
        }
        
    except Exception as e:
        print(f"Error en obtener_estadisticas_citas: {str(e)}")
        return {
            'total_citas': 0,
            'citas_hoy': 0,
            'por_estado': {
                'agendadas': 0,
                'atendidas': 0,
                'canceladas': 0,
                'no_atendidas': 0
            },
            'por_tipo': {
                'presenciales': 0,
                'virtuales': 0
            },
            'por_especialidad': {},
            'error': str(e)
        }

def obtener_citas_hoy():
    """
    Obtiene las citas programadas para el día actual.
    """
    try:
        from app import mysql
        citas_hoy = Cita.obtener_citas_hoy(mysql)
        return citas_hoy
        
    except Exception as e:
        print(f"Error en obtener_citas_hoy: {str(e)}")
        return []

def obtener_detalle_cita(cita_id):
    """
    Obtiene información detallada de una cita específica.
    """
    try:
        from app import mysql
        
        resultado = Cita.obtener_cita(mysql, cita_id)
        if not resultado['success']:
            return {
                'exito': False,
                'error': resultado['error']
            }
        
        cita = resultado['cita']
        
        # Obtener información adicional del paciente y médico
        paciente = Paciente.obtener_por_id(mysql, cita['paciente_id'])
        profesional = Profesional.obtener_por_id(mysql, cita['medico_id'])
        
        return {
            'exito': True,
            'cita': {
                'id': cita['id'],
                'paciente': {
                    'id': paciente['id'] if paciente else None,
                    'nombre_completo': f"{paciente['nombres']} {paciente['apellidos']}" if paciente else 'N/A',
                    'dni': paciente['dni'] if paciente else 'N/A',
                    'telefono': paciente.get('telefono', '') if paciente else '',
                    'email': paciente.get('email', '') if paciente else ''
                },
                'medico': {
                    'id': profesional['id'] if profesional else None,
                    'nombre_completo': Profesional.obtener_nombre_completo(profesional) if profesional else 'N/A',
                    'especialidad': profesional['especialidad'] if profesional else 'N/A',
                    'telefono': profesional.get('telefono', '') if profesional else '',
                    'email': profesional.get('email', '') if profesional else ''
                },
                'fecha_cita': cita['fecha_cita'].strftime('%d/%m/%Y') if hasattr(cita['fecha_cita'], 'strftime') else str(cita['fecha_cita']),
                'fecha_cita_iso': cita['fecha_cita'].isoformat() if hasattr(cita['fecha_cita'], 'isoformat') else str(cita['fecha_cita']),
                'hora_inicio': cita['hora_inicio'].strftime('%H:%M') if hasattr(cita['hora_inicio'], 'strftime') else str(cita['hora_inicio']),
                'hora_fin': cita['hora_fin'].strftime('%H:%M') if hasattr(cita['hora_fin'], 'strftime') else str(cita['hora_fin']),
                'horario_completo': Cita.formatear_horario_completo(cita['hora_inicio'], cita['hora_fin']),
                'duracion_formateada': Cita.formatear_duracion(cita['duracion_minutos']),
                'tipo': cita['tipo'],
                'estado': cita['estado'],
                'especialidad': cita['especialidad'],
                'consultorio': cita['consultorio'],
                'enlace_virtual': cita['enlace_virtual'],
                'motivo_consulta': cita['motivo_consulta'],
                'observaciones': cita['observaciones'],
                'fecha_creacion': cita['fecha_creacion'].strftime('%d/%m/%Y %H:%M') if hasattr(cita.get('fecha_creacion'), 'strftime') else None
            }
        }
        
    except Exception as e:
        print(f"Error en obtener_detalle_cita: {str(e)}")
        return {
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }

def cancelar_cita_admin(cita_id):
    """
    Cancela una cita desde el panel de administración.
    """
    try:
        from app import mysql
        
        resultado = Cita.cancelar_cita(mysql, cita_id)
        
        if resultado['success']:
            return {
                'exito': True,
                'mensaje': resultado['message']
            }
        else:
            return {
                'exito': False,
                'error': resultado['error']
            }
        
    except Exception as e:
        print(f"Error en cancelar_cita_admin: {str(e)}")
        return {
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }

def actualizar_estado_cita(cita_id, nuevo_estado):
    """
    Actualiza el estado de una cita.
    """
    try:
        from app import mysql
        
        estados_validos = ['AGENDADA', 'ATENDIDA', 'NO_ATENDIDA', 'CANCELADA']
        if nuevo_estado not in estados_validos:
            return {
                'exito': False,
                'error': f'Estado no válido. Debe ser uno de: {", ".join(estados_validos)}'
            }
        
        resultado = Cita.actualizar_estado_cita(mysql, cita_id, nuevo_estado)
        
        if resultado['success']:
            return {
                'exito': True,
                'mensaje': resultado['message'],
                'nuevo_estado': nuevo_estado
            }
        else:
            return {
                'exito': False,
                'error': resultado['error']
            }
        
    except Exception as e:
        print(f"Error en actualizar_estado_cita: {str(e)}")
        return {
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }