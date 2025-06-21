# controllers/paciente_citas.py

from models.cita import Cita
from flask import session

def crear_cita_paciente(datos_cita):
    """
    Crea una nueva cita para el paciente autenticado.
    """
    try:
        # Validaciones básicas
        campos_requeridos = ['paciente_id', 'horario_id', 'enfermedad_id', 'tipo', 'motivo_consulta']
        for campo in campos_requeridos:
            if not datos_cita.get(campo):
                return {
                    'exito': False,
                    'error': f'El campo {campo} es requerido'
                }
        
        # Validar que el paciente_id corresponde al usuario autenticado (seguridad)
        # usuario_autenticado = session.get('user_id')
        # if datos_cita['paciente_id'] != usuario_autenticado:
        #     return {
        #         'exito': False,
        #         'error': 'Solo puedes crear citas para tu propio perfil'
        #     }
        
        # Validar valores de tipo
        tipos_validos = ['PRESENCIAL', 'VIRTUAL']
        if datos_cita['tipo'] not in tipos_validos:
            return {
                'exito': False,
                'error': f'Tipo debe ser uno de: {", ".join(tipos_validos)}'
            }
        
        # Crear la cita usando el modelo
        resultado = Cita.crear_cita(datos_cita)
        
        if resultado['success']:
            return {
                'exito': True,
                'mensaje': resultado['message'],
                'cita_id': resultado['cita_id'],
                'cita': resultado.get('cita')
            }
        else:
            return {
                'exito': False,
                'error': resultado['error']
            }
        
    except Exception as e:
        print(f"Error en crear_cita_paciente: {str(e)}")  # Para debug
        return {
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }

def obtener_cita_paciente(cita_id):
    """
    Obtiene una cita específica del paciente autenticado.
    """
    try:
        paciente_id = session.get('user_id')
        if not paciente_id:
            return {
                'exito': False,
                'error': 'Sesión de paciente no válida'
            }
        
        resultado = Cita.obtener_cita(cita_id)
        
        if not resultado['success']:
            return {
                'exito': False,
                'error': resultado['error']
            }
        
        # Verificar que la cita pertenece al paciente logueado
        if resultado['cita'].paciente_id != paciente_id:
            return {
                'exito': False,
                'error': 'No tienes autorización para ver esta cita'
            }
        
        return {
            'exito': True,
            'cita': {
                'id': resultado['cita'].id,
                'fecha_cita': resultado['cita'].fecha_cita.isoformat(),
                'hora_inicio': resultado['cita'].hora_inicio.strftime('%H:%M'),
                'hora_fin': resultado['cita'].hora_fin.strftime('%H:%M'),
                'horario_completo': resultado['cita'].horario_completo,
                'duracion_formateada': resultado['cita'].duracion_formateada,
                'tipo': resultado['cita'].tipo,
                'consultorio': resultado['cita'].consultorio,
                'especialidad': resultado['cita'].especialidad,
                'estado': resultado['cita'].estado,
                'motivo_consulta': resultado['cita'].motivo_consulta,
                'observaciones': resultado['cita'].observaciones,
                'enlace_virtual': resultado['cita'].enlace_virtual
            }
        }
        
    except Exception as e:
        print(f"Error en obtener_cita_paciente: {str(e)}")  # Para debug
        return {
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }

def cancelar_cita_paciente(cita_id):
    """
    Cancela una cita del paciente autenticado.
    """
    try:
        paciente_id = session.get('user_id')
        if not paciente_id:
            return {
                'exito': False,
                'error': 'Sesión de paciente no válida'
            }
        
        # Verificar que la cita existe y pertenece al paciente
        cita_info = Cita.obtener_cita(cita_id)
        if not cita_info['success']:
            return {
                'exito': False,
                'error': 'Cita no encontrada'
            }
        
        if cita_info['cita'].paciente_id != paciente_id:
            return {
                'exito': False,
                'error': 'No tienes autorización para cancelar esta cita'
            }
        
        if cita_info['cita'].estado == 'CANCELADA':
            return {
                'exito': False,
                'error': 'La cita ya está cancelada'
            }
        
        # Cancelar la cita
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
        print(f"Error en cancelar_cita_paciente: {str(e)}")  # Para debug
        return {
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }

def listar_citas_paciente(estado_filtro=None):
    """
    Lista todas las citas del paciente autenticado.
    """
    try:
        paciente_id = session.get('user_id')
        if not paciente_id:
            return {
                'exito': False,
                'error': 'Sesión de paciente no válida'
            }
        
        # Obtener citas del paciente
        resultado = Cita.listar_citas_paciente(paciente_id, estado_filtro)
        
        if not resultado['success']:
            return {
                'exito': False,
                'error': resultado['error']
            }
        
        # Formatear las citas
        citas_formateadas = []
        for cita in resultado['citas']:
            citas_formateadas.append({
                'id': cita.id,
                'fecha_cita': cita.fecha_cita.isoformat(),
                'hora_inicio': cita.hora_inicio.strftime('%H:%M'),
                'hora_fin': cita.hora_fin.strftime('%H:%M'),
                'horario_completo': cita.horario_completo,
                'duracion_formateada': cita.duracion_formateada,
                'tipo': cita.tipo,
                'consultorio': cita.consultorio,
                'especialidad': cita.especialidad,
                'estado': cita.estado,
                'motivo_consulta': cita.motivo_consulta,
                'enlace_virtual': cita.enlace_virtual
            })
        
        return {
            'exito': True,
            'citas': citas_formateadas,
            'total': resultado['total'],
            'filtro_estado': estado_filtro
        }
        
    except Exception as e:
        print(f"Error en listar_citas_paciente: {str(e)}")  # Para debug
        return {
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }

def obtener_resumen_dashboard_paciente():
    """
    Obtiene información resumida para el dashboard del paciente.
    """
    try:
        paciente_id = session.get('user_id')
        if not paciente_id:
            return {
                'exito': False,
                'error': 'Sesión de paciente no válida'
            }
        
        # Obtener estadísticas básicas
        resultado_citas = Cita.listar_citas_paciente(paciente_id)
        
        if not resultado_citas['success']:
            return {
                'exito': False,
                'error': 'Error al obtener información del paciente'
            }
        
        citas = resultado_citas['citas']
        
        # Calcular estadísticas
        total_citas = len(citas)
        citas_agendadas = len([c for c in citas if c.estado == 'AGENDADA'])
        citas_atendidas = len([c for c in citas if c.estado == 'ATENDIDA'])
        citas_canceladas = len([c for c in citas if c.estado == 'CANCELADA'])
        
        # Próxima cita
        from datetime import date
        proxima_cita = None
        citas_futuras = [c for c in citas if c.fecha_cita >= date.today() and c.estado == 'AGENDADA']
        if citas_futuras:
            proxima_cita = min(citas_futuras, key=lambda x: (x.fecha_cita, x.hora_inicio))
        
        return {
            'exito': True,
            'resumen': {
                'total_citas': total_citas,
                'citas_agendadas': citas_agendadas,
                'citas_atendidas': citas_atendidas,
                'citas_canceladas': citas_canceladas,
                'proxima_cita': {
                    'id': proxima_cita.id,
                    'fecha': proxima_cita.fecha_cita.isoformat(),
                    'hora': proxima_cita.hora_inicio.strftime('%H:%M'),
                    'especialidad': proxima_cita.especialidad,
                    'tipo': proxima_cita.tipo
                } if proxima_cita else None
            }
        }
        
    except Exception as e:
        print(f"Error en obtener_resumen_dashboard_paciente: {str(e)}")  # Para debug
        return {
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }