# controllers/admin_horarios.py 

from models.admin_horarios import HorarioDisponible, PlantillaHorario
from models.actores import Profesional
from models.admin_dashboard import Cita
from datetime import datetime, date, timedelta  

def obtener_horarios_semana(fecha_referencia=None):
    """
    Retorna horarios de una semana organizados por día para el calendario.
    """
    try:
        if not fecha_referencia:
            fecha_referencia = date.today()
        
        # Calcular lunes de la semana
        dias_hasta_lunes = fecha_referencia.weekday()
        lunes = fecha_referencia - timedelta(days=dias_hasta_lunes)
        viernes = lunes + timedelta(days=4)
        
        # Obtener horarios de la semana
        horarios_semana = HorarioDisponible.obtener_horarios_semana(lunes, viernes)
        
        # Inicializar estructura de días
        datos_dias = {}
        nombres_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        
        for i in range(5):  # Lunes a Viernes
            fecha_dia = lunes + timedelta(days=i)
            datos_dias[fecha_dia.isoformat()] = {
                'fecha': fecha_dia,
                'nombre_dia': nombres_dias[i],
                'horarios': []
            }
        
        # Organizar horarios por día
        for horario in horarios_semana:
            fecha_iso = horario.fecha.isoformat()
            if fecha_iso in datos_dias:
                datos_dias[fecha_iso]['horarios'].append({
                    'id': horario.id,
                    'hora_inicio': horario.hora_inicio.strftime('%H:%M'),
                    'hora_fin': horario.hora_fin.strftime('%H:%M'),
                    'medico_nombre': horario.nombre_medico_completo,
                    'tipo': horario.tipo,
                    'consultorio': horario.consultorio or 'Virtual',
                    'ocupado': horario.esta_ocupado,
                    'observaciones': horario.observaciones or ''
                })
        
        return {
            'lunes': lunes,
            'viernes': viernes,
            'datos_dias': datos_dias
        }
        
    except Exception as e:
        print(f"Error en obtener_horarios_semana: {str(e)}")  # Para debug
        raise e

def obtener_medicos_activos():
    """
    Retorna lista de profesionales activos para formularios de horarios.
    """
    try:
        profesionales = Profesional.query.filter_by(estado='ACTIVO').order_by(
            Profesional.nombres, Profesional.apellidos
        ).all()
        
        return [{
            'id': prof.id,
            'nombre_completo': f"Dr. {prof.nombres} {prof.apellidos}",
            'especialidad': prof.especialidad,
            'email': prof.email if prof.email else None
        } for prof in profesionales]
        
    except Exception as e:
        print(f"Error en obtener_medicos_activos: {str(e)}")  # Para debug
        raise e

def crear_horario_disponible(datos_horario):
    """
    Crea un nuevo horario disponible con validaciones completas.
    """
    try:
        # Validaciones básicas
        campos_requeridos = ['medico_id', 'fecha', 'hora_inicio', 'hora_fin', 'tipo']
        for campo in campos_requeridos:
            if not datos_horario.get(campo):
                return {
                    'exito': False,
                    'error': f'El campo {campo} es requerido'
                }
        
        # Validar que el profesional existe y está activo
        profesional = Profesional.query.filter_by(
            id=datos_horario['medico_id'], 
            estado='ACTIVO'
        ).first()
        
        if not profesional:
            return {
                'exito': False,
                'error': 'El profesional seleccionado no existe o no está activo'
            }
        
        # Convertir y validar fecha/horas
        try:
            fecha = datetime.strptime(datos_horario['fecha'], '%Y-%m-%d').date()
            hora_inicio = datetime.strptime(datos_horario['hora_inicio'], '%H:%M').time()
            hora_fin = datetime.strptime(datos_horario['hora_fin'], '%H:%M').time()
        except ValueError as ve:
            return {
                'exito': False,
                'error': f'Formato de fecha u hora inválido: {str(ve)}'
            }
        
        # Validar que la fecha no sea en el pasado
        if fecha < date.today():
            return {
                'exito': False,
                'error': 'No se pueden crear horarios en fechas pasadas'
            }
        
        # Validar rango de horas
        if hora_fin <= hora_inicio:
            return {
                'exito': False,
                'error': 'La hora de fin debe ser posterior a la hora de inicio'
            }
        
        # Verificar conflictos de horarios
        conflicto = HorarioDisponible.verificar_conflicto_horario(
            datos_horario['medico_id'], fecha, hora_inicio, hora_fin
        )
        
        if conflicto:
            return {
                'exito': False,
                'error': f'Conflicto de horarios: ya existe un horario de {conflicto.hora_inicio.strftime("%H:%M")} a {conflicto.hora_fin.strftime("%H:%M")}'
            }
        
        # Crear el horario
        # Calcular duración para determinar si es slot individual o rango
        inicio_dt = datetime.combine(fecha, hora_inicio)
        fin_dt = datetime.combine(fecha, hora_fin)
        duracion_horas = (fin_dt - inicio_dt).total_seconds() / 3600
        
        if duracion_horas == 1:
            # Crear un solo slot de 1 hora - usar tu función existente
            nuevo_horario = HorarioDisponible.crear_horario(datos_horario)
            
            return { 
                'exito': True,
                'mensaje': 'Slot de 1 hora creado exitosamente',
                'slots_creados': 1,
                'horario': {
                    'id': nuevo_horario.id,
                    'medico_nombre': nuevo_horario.nombre_medico_completo,
                    'fecha': nuevo_horario.fecha.isoformat(),
                    'hora_inicio': nuevo_horario.hora_inicio.strftime('%H:%M'),
                    'hora_fin': nuevo_horario.hora_fin.strftime('%H:%M'),
                    'tipo': nuevo_horario.tipo,
                    'consultorio': nuevo_horario.consultorio
                }
            }
        else:
            # Crear múltiples slots de 1 hora - usar nueva función
            slots_creados = HorarioDisponible.crear_horarios_rango(datos_horario)
            
            return { 
                'exito': True,
                'mensaje': f'{len(slots_creados)} slots de 1 hora creados exitosamente',
                'slots_creados': len(slots_creados),
                'horarios': [{
                    'id': slot.id,
                    'medico_nombre': slot.nombre_medico_completo,
                    'fecha': slot.fecha.isoformat(),
                    'hora_inicio': slot.hora_inicio.strftime('%H:%M'),
                    'hora_fin': slot.hora_fin.strftime('%H:%M'),
                    'tipo': slot.tipo,
                    'consultorio': slot.consultorio
                } for slot in slots_creados]
            }
        
    except ValueError as ve:
        return {
            'exito': False,
            'error': str(ve)
        }
    except Exception as e:
        print(f"Error en crear_horario_disponible: {str(e)}")
        return {
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }

def obtener_detalle_horario(horario_id):
    """
    Obtiene información detallada de un horario específico.
    """
    try:
        horario = HorarioDisponible.obtener_por_id(horario_id)
        
        if not horario:
            return {
                'exito': False,
                'error': 'Horario no encontrado'
            }
        
        # Contar citas asociadas
        #total_citas = len(horario.citas) if horario.citas else 0
        
        return {
            'exito': True,
            'horario': {
                'id': horario.id,
                'medico_id': horario.medico_id,
                'medico_nombre': horario.nombre_medico_completo,
                'especialidad': horario.medico.especialidad,
                'fecha': horario.fecha.isoformat(),
                'hora_inicio': horario.hora_inicio.strftime('%H:%M'),
                'hora_fin': horario.hora_fin.strftime('%H:%M'),
                'tipo': horario.tipo,
                'consultorio': horario.consultorio or 'Virtual',
                'duracion_cita': horario.duracion_cita,
                'estado': horario.estado,
                'observaciones': horario.observaciones or '',
                'ocupado': horario.esta_ocupado
                #'total_citas': total_citas
            }
        }
        
    except Exception as e:
        print(f"Error en obtener_detalle_horario: {str(e)}")  # Para debug
        return {
            'exito': False,
            'error': f'Error al obtener horario: {str(e)}'
        }

def eliminar_horario_disponible(horario_id):
    """
    Elimina un horario disponible con validaciones de seguridad.
    """
    try:
        resultado = HorarioDisponible.eliminar_horario(horario_id)
        
        if resultado:
            return {
                'exito': True,
                'mensaje': 'Horario eliminado exitosamente'
            }
        else:
            return {
                'exito': False,
                'error': 'Horario no encontrado'
            }
            
    except ValueError as e:
        return {
            'exito': False,
            'error': str(e)
        }
    except Exception as e:
        print(f"Error en eliminar_horario_disponible: {str(e)}")  # Para debug
        return {
            'exito': False,
            'error': f'Error al eliminar horario: {str(e)}'
        }

def obtener_estadisticas_horarios():
    """
    Retorna estadísticas resumidas del sistema de horarios.
    """
    try:
        # Total de horarios activos
        horarios_activos = HorarioDisponible.query.filter_by(estado='ACTIVO').all()
        total_horarios = len(horarios_activos)
        
        # Contar ocupados vs disponibles
        horarios_ocupados = sum(1 for h in horarios_activos if h.esta_ocupado)
        horarios_disponibles = total_horarios - horarios_ocupados
        
        # Estadísticas por tipo
        stats_tipo = {}
        for horario in horarios_activos:
            tipo = horario.tipo
            stats_tipo[tipo] = stats_tipo.get(tipo, 0) + 1
        
        # Estadísticas por médico (top 5)
        stats_medico = {}
        for horario in horarios_activos:
            medico_nombre = horario.nombre_medico_completo
            stats_medico[medico_nombre] = stats_medico.get(medico_nombre, 0) + 1
        
        # Ordenar médicos por cantidad de horarios
        stats_medico_ordenado = dict(
            sorted(stats_medico.items(), key=lambda x: x[1], reverse=True)[:5]
        )
        
        return {
            'total_horarios': total_horarios,
            'horarios_ocupados': horarios_ocupados,
            'horarios_disponibles': horarios_disponibles,
            'por_tipo': stats_tipo,
            'por_medico': stats_medico_ordenado
        }
        
    except Exception as e:
        print(f"Error en obtener_estadisticas_horarios: {str(e)}")  # Para debug
        return {
            'total_horarios': 0,
            'horarios_ocupados': 0,
            'horarios_disponibles': 0,
            'por_tipo': {},
            'por_medico': {},
            'error': str(e)
        }

def actualizar_horario_disponible(datos_horario):
    """
    Actualiza un horario disponible existente con validaciones completas.
    """
    try:
        horario_id = datos_horario.get('horario_id')
        if not horario_id:
            return {
                'exito': False,
                'error': 'ID de horario es requerido'
            }

        # Validaciones básicas
        campos_requeridos = ['medico_id', 'fecha', 'hora_inicio', 'hora_fin', 'tipo']
        for campo in campos_requeridos:
            if not datos_horario.get(campo):
                return {
                    'exito': False,
                    'error': f'El campo {campo} es requerido'
                }
        
        # Verificar que el horario existe
        horario_existente = HorarioDisponible.obtener_por_id(horario_id)
        if not horario_existente:
            return {
                'exito': False,
                'error': 'El horario no existe'
            }

        # Validar que el profesional existe y está activo
        profesional = Profesional.query.filter_by(
            id=datos_horario['medico_id'], 
            estado='ACTIVO'
        ).first()
        
        if not profesional:
            return {
                'exito': False,
                'error': 'El profesional seleccionado no existe o no está activo'
            }
        
        # Convertir y validar fecha/horas
        try:
            fecha = datetime.strptime(datos_horario['fecha'], '%Y-%m-%d').date()
            hora_inicio = datetime.strptime(datos_horario['hora_inicio'], '%H:%M').time()
            hora_fin = datetime.strptime(datos_horario['hora_fin'], '%H:%M').time()
        except ValueError as ve:
            return {
                'exito': False,
                'error': f'Formato de fecha u hora inválido: {str(ve)}'
            }
        
        # Validar que la fecha no sea en el pasado (solo si se cambia a una fecha futura)
        if fecha < date.today():
            return {
                'exito': False,
                'error': 'No se pueden programar horarios en fechas pasadas'
            }
        
        # Validar rango de horas
        if hora_fin <= hora_inicio:
            return {
                'exito': False,
                'error': 'La hora de fin debe ser posterior a la hora de inicio'
            }
        
        # Verificar conflictos de horarios (excluyendo el horario actual)
        conflicto = HorarioDisponible.verificar_conflicto_horario(
            datos_horario['medico_id'], fecha, hora_inicio, hora_fin, excluir_id=horario_id
        )
        
        if conflicto:
            return {
                'exito': False,
                'error': f'Conflicto de horarios: ya existe un horario de {conflicto.hora_inicio.strftime("%H:%M")} a {conflicto.hora_fin.strftime("%H:%M")}'
            }
        
        # Verificar si tiene citas agendadas y la modificación afecta el horario
        citas_existentes = len([cita for cita in horario_existente.citas if cita.estado == 'AGENDADA'])
        
        if citas_existentes > 0:
            # Si tiene citas, verificar que los cambios no afecten el horario base
            hora_inicio_original = horario_existente.hora_inicio
            hora_fin_original = horario_existente.hora_fin
            
            if hora_inicio > hora_inicio_original or hora_fin < hora_fin_original:
                return {
                    'exito': False,
                    'error': f'No se puede reducir el horario porque tiene {citas_existentes} cita(s) agendada(s). Solo se puede extender.'
                }
        
        # Actualizar el horario
        horario_actualizado = HorarioDisponible.actualizar_horario(horario_id, datos_horario)
        
        return {
            'exito': True,
            'mensaje': 'Horario actualizado exitosamente',
            'horario': {
                'id': horario_actualizado.id,
                'medico_nombre': horario_actualizado.nombre_medico_completo,
                'fecha': horario_actualizado.fecha.isoformat(),
                'hora_inicio': horario_actualizado.hora_inicio.strftime('%H:%M'),
                'hora_fin': horario_actualizado.hora_fin.strftime('%H:%M'),
                'tipo': horario_actualizado.tipo,
                'consultorio': horario_actualizado.consultorio
            }
        }
        
    except Exception as e:
        print(f"Error en actualizar_horario_disponible: {str(e)}")  # Para debug
        return {
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }
        