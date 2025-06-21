# controllers/admin_citas_medicas.py

from models.admin_citas_medicas import AdminCitasMedicas
from models.actores import Profesional
from datetime import date

def obtener_citas_medicas():
    """
    Obtiene todas las citas médicas para mostrar en la tabla.
    """
    try:
        citas = AdminCitasMedicas.obtener_todas_citas()
        
        # Formatear datos para el frontend
        citas_formateadas = []
        for cita in citas:
            from models.actores import Paciente
            paciente = Paciente.query.get(cita.paciente_id)
            profesional = Profesional.query.get(cita.medico_id)
            
            citas_formateadas.append({
                'id': cita.id,
                'paciente_nombre': paciente.nombre_completo if paciente else 'N/A',
                'paciente_dni': paciente.dni if paciente else 'N/A',
                'medico_nombre': profesional.nombre_completo if profesional else 'N/A',
                'especialidad': cita.especialidad,
                'fecha_cita': cita.fecha_cita.strftime('%d/%m/%Y'),
                'fecha_cita_iso': cita.fecha_cita.isoformat(),
                'hora_inicio': cita.hora_inicio.strftime('%H:%M'),
                'hora_fin': cita.hora_fin.strftime('%H:%M'),
                'horario_completo': cita.horario_completo,
                'tipo': cita.tipo,
                'estado': cita.estado,
                'consultorio': cita.consultorio or 'Virtual',
                'enlace_virtual': cita.enlace_virtual,
                'motivo_consulta': cita.motivo_consulta or '',
                'observaciones': cita.observaciones or ''
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
        resultado = AdminCitasMedicas.obtener_citas_con_filtros(
            fecha=fecha,
            medico_id=medico_id,
            especialidad=especialidad,
            estado=estado,
            tipo=tipo,
            busqueda=busqueda,
            page=page,
            per_page=per_page
        )
        
        if resultado['success']:
            return {
                'exito': True,
                'citas': resultado['citas'],
                'pagination': resultado['pagination']
            }
        else:
            return {
                'exito': False,
                'error': resultado['error'],
                'citas': [],
                'pagination': {}
            }
        
    except Exception as e:
        print(f"Error en obtener_citas_con_filtros: {str(e)}")
        return {
            'exito': False,
            'error': f'Error interno: {str(e)}',
            'citas': [],
            'pagination': {}
        }

def obtener_medicos_para_filtro():
    """
    Obtiene lista de médicos activos para el filtro.
    """
    try:
        medicos = Profesional.query.filter_by(estado='ACTIVO').order_by(
            Profesional.nombres, Profesional.apellidos
        ).all()
        
        return [{
            'id': medico.id,
            'nombre_completo': medico.nombre_completo,
            'especialidad': medico.especialidad
        } for medico in medicos]
        
    except Exception as e:
        print(f"Error en obtener_medicos_para_filtro: {str(e)}")
        return []

def obtener_estadisticas_citas():
    """
    Obtiene estadísticas resumidas de las citas médicas.
    """
    try:
        estadisticas = AdminCitasMedicas.obtener_estadisticas_citas()
        
        if 'error' in estadisticas:
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
                'error': estadisticas['error']
            }
        
        return estadisticas
        
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
        citas_hoy = AdminCitasMedicas.obtener_citas_hoy()
        return citas_hoy
        
    except Exception as e:
        print(f"Error en obtener_citas_hoy: {str(e)}")
        return []

def obtener_detalle_cita(cita_id):
    """
    Obtiene información detallada de una cita específica.
    """
    try:
        from models.cita import Cita
        from models.actores import Paciente
        
        cita = Cita.query.get(cita_id)
        if not cita:
            return {
                'exito': False,
                'error': 'Cita no encontrada'
            }
        
        paciente = Paciente.query.get(cita.paciente_id)
        profesional = Profesional.query.get(cita.medico_id)
        
        return {
            'exito': True,
            'cita': {
                'id': cita.id,
                'paciente': {
                    'id': paciente.id,
                    'nombre_completo': paciente.nombre_completo,
                    'dni': paciente.dni,
                    'telefono': paciente.telefono,
                    'email': paciente.email
                },
                'medico': {
                    'id': profesional.id,
                    'nombre_completo': profesional.nombre_completo,
                    'especialidad': profesional.especialidad,
                    'telefono': profesional.telefono,
                    'email': profesional.email
                },
                'fecha_cita': cita.fecha_cita.strftime('%d/%m/%Y'),
                'fecha_cita_iso': cita.fecha_cita.isoformat(),
                'hora_inicio': cita.hora_inicio.strftime('%H:%M'),
                'hora_fin': cita.hora_fin.strftime('%H:%M'),
                'horario_completo': cita.horario_completo,
                'duracion_formateada': cita.duracion_formateada,
                'tipo': cita.tipo,
                'estado': cita.estado,
                'especialidad': cita.especialidad,
                'consultorio': cita.consultorio,
                'enlace_virtual': cita.enlace_virtual,
                'motivo_consulta': cita.motivo_consulta,
                'observaciones': cita.observaciones,
                'fecha_creacion': cita.fecha_creacion.strftime('%d/%m/%Y %H:%M') if cita.fecha_creacion else None
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
        from models.cita import Cita
        
        resultado = Cita.cancelar_cita(cita_id)
        
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
        from models.cita import Cita
        
        cita = Cita.query.get(cita_id)
        if not cita:
            return {
                'exito': False,
                'error': 'Cita no encontrada'
            }
        
        estados_validos = ['AGENDADA', 'ATENDIDA', 'NO_ATENDIDA', 'CANCELADA']
        if nuevo_estado not in estados_validos:
            return {
                'exito': False,
                'error': f'Estado no válido. Debe ser uno de: {", ".join(estados_validos)}'
            }
        
        cita.estado = nuevo_estado
        from models import db
        db.session.commit()
        
        return {
            'exito': True,
            'mensaje': f'Estado de cita actualizado a {nuevo_estado}',
            'nuevo_estado': nuevo_estado
        }
        
    except Exception as e:
        from models import db
        db.session.rollback()
        print(f"Error en actualizar_estado_cita: {str(e)}")
        return {
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }