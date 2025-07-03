# controllers/admin_horarios.py 

from models.admin_horarios import HorarioDisponible, PlantillaHorario
from models.actores import Profesional
from models.cita import Cita
from datetime import datetime, date, timedelta

def obtener_horarios_semana(fecha_referencia=None):
    """
    Retorna horarios de una semana organizados por día para el calendario.
    """
    try:
        from app import mysql
        
        if not fecha_referencia:
            fecha_referencia = date.today()
        
        # Calcular lunes de la semana
        dias_hasta_lunes = fecha_referencia.weekday()
        lunes = fecha_referencia - timedelta(days=dias_hasta_lunes)
        viernes = lunes + timedelta(days=4)
         
        print(f"Buscando horarios entre {lunes} y {viernes}")
        
        # Obtener horarios de la semana
        horarios_semana = HorarioDisponible.obtener_horarios_semana(mysql, lunes, viernes)
        
        print(f"Horarios encontrados: {len(horarios_semana)}")
        for h in horarios_semana:
            print(f"  - ID: {h['id']}, Fecha: {h['fecha']}, Hora: {h['hora_inicio']}-{h['hora_fin']}, Médico: {h['nombres']} {h['apellidos']}")
        
        # Inicializar estructura de días
        datos_dias = {}
        nombres_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        
        for i in range(5):  # Lunes a Viernes
            fecha_dia = lunes + timedelta(days=i)
            fecha_str = fecha_dia.isoformat()
            datos_dias[fecha_str] = {
                'fecha': fecha_dia,
                'nombre_dia': nombres_dias[i],
                'horarios': []
            }
        
        # Organizar horarios por día
        for horario in horarios_semana:
            # Convertir fecha del horario a string ISO
            if hasattr(horario['fecha'], 'isoformat'):
                fecha_iso = horario['fecha'].isoformat()
            else:
                # Si ya es string, convertir a date y luego a ISO
                if isinstance(horario['fecha'], str):
                    fecha_obj = datetime.strptime(horario['fecha'], '%Y-%m-%d').date()
                    fecha_iso = fecha_obj.isoformat()
                else:
                    fecha_iso = str(horario['fecha'])
            
            print(f"Procesando horario para fecha: {fecha_iso}")
            
            if fecha_iso in datos_dias:
                # Verificar si el horario está ocupado
                esta_ocupado = HorarioDisponible.esta_ocupado(mysql, horario['id'])
                
                horario_info = {
                    'id': horario['id'],
                    'hora_inicio': horario['hora_inicio'].strftime('%H:%M') if hasattr(horario['hora_inicio'], 'strftime') else str(horario['hora_inicio']),
                    'hora_fin': horario['hora_fin'].strftime('%H:%M') if hasattr(horario['hora_fin'], 'strftime') else str(horario['hora_fin']),
                    'medico_nombre': f"Dr. {horario['nombres']} {horario['apellidos']}",
                    'tipo': horario['tipo'],
                    'consultorio': horario.get('consultorio') or 'Virtual',
                    'ocupado': esta_ocupado,
                    'observaciones': horario.get('observaciones') or ''
                }
                
                datos_dias[fecha_iso]['horarios'].append(horario_info)
                print(f"  - Agregado horario: {horario_info}")
            else:
                print(f"  - Fecha {fecha_iso} no está en el rango de la semana")
        
        return {
            'lunes': lunes,
            'viernes': viernes,
            'datos_dias': datos_dias
        }
        
    except Exception as e:
        print(f"Error en obtener_horarios_semana: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e
    
def obtener_medicos_activos():
    """
    Retorna lista de profesionales activos para formularios de horarios.
    """
    try:
        from app import mysql
        
        profesionales = Profesional.obtener_medicos_activos(mysql)
        
        return [{
            'id': prof['id'],
            'nombre_completo': f"Dr. {prof['nombres']} {prof['apellidos']}",
            'especialidad': prof['especialidad'],
            'email': prof.get('email') if prof.get('email') else None
        } for prof in profesionales]
        
    except Exception as e:
        print(f"Error en obtener_medicos_activos: {str(e)}")
        raise e

def crear_horario_disponible(datos_horario):
    """
    Crea un nuevo horario disponible con validaciones completas.
    """
    try:
        from app import mysql
        
        # Validaciones básicas
        campos_requeridos = ['medico_id', 'fecha', 'hora_inicio', 'hora_fin', 'tipo']
        for campo in campos_requeridos:
            if not datos_horario.get(campo):
                return {
                    'exito': False,
                    'error': f'El campo {campo} es requerido'
                }
        
        # Validar que el profesional existe y está activo
        profesional = Profesional.obtener_por_id(mysql, datos_horario['medico_id'])
        
        if not profesional or profesional.get('estado') != 'ACTIVO':
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
        tiene_conflicto = HorarioDisponible.verificar_conflicto_horario(
            mysql, datos_horario['medico_id'], fecha, hora_inicio, hora_fin
        )
        
        if tiene_conflicto:
            return {
                'exito': False,
                'error': 'Conflicto de horarios: ya existe un horario en ese rango de tiempo'
            }
        
        # Calcular duración para determinar si es slot individual o rango
        inicio_dt = datetime.combine(fecha, hora_inicio)
        fin_dt = datetime.combine(fecha, hora_fin)
        duracion_horas = (fin_dt - inicio_dt).total_seconds() / 3600
        
        if duracion_horas == 1:
            # Crear un solo slot de 1 hora
            horario_id = HorarioDisponible.crear_horario(mysql, datos_horario)
            horario_creado = HorarioDisponible.obtener_por_id(mysql, horario_id)
            
            return { 
                'exito': True,
                'mensaje': 'Slot de 1 hora creado exitosamente',
                'slots_creados': 1,
                'horario': {
                    'id': horario_creado['id'],
                    'medico_nombre': f"Dr. {horario_creado['nombres']} {horario_creado['apellidos']}",
                    'fecha': horario_creado['fecha'].isoformat() if hasattr(horario_creado['fecha'], 'isoformat') else str(horario_creado['fecha']),
                    'hora_inicio': horario_creado['hora_inicio'].strftime('%H:%M') if hasattr(horario_creado['hora_inicio'], 'strftime') else str(horario_creado['hora_inicio']),
                    'hora_fin': horario_creado['hora_fin'].strftime('%H:%M') if hasattr(horario_creado['hora_fin'], 'strftime') else str(horario_creado['hora_fin']),
                    'tipo': horario_creado['tipo'],
                    'consultorio': horario_creado.get('consultorio')
                }
            }
        else:
            # Crear múltiples slots de 1 hora
            slots_ids = HorarioDisponible.crear_horarios_rango(mysql, datos_horario)
            
            horarios_creados = []
            for slot_id in slots_ids:
                horario = HorarioDisponible.obtener_por_id(mysql, slot_id)
                horarios_creados.append({
                    'id': horario['id'],
                    'medico_nombre': f"Dr. {horario['nombres']} {horario['apellidos']}",
                    'fecha': horario['fecha'].isoformat() if hasattr(horario['fecha'], 'isoformat') else str(horario['fecha']),
                    'hora_inicio': horario['hora_inicio'].strftime('%H:%M') if hasattr(horario['hora_inicio'], 'strftime') else str(horario['hora_inicio']),
                    'hora_fin': horario['hora_fin'].strftime('%H:%M') if hasattr(horario['hora_fin'], 'strftime') else str(horario['hora_fin']),
                    'tipo': horario['tipo'],
                    'consultorio': horario.get('consultorio')
                })
            
            return { 
                'exito': True,
                'mensaje': f'{len(slots_ids)} slots de 1 hora creados exitosamente',
                'slots_creados': len(slots_ids),
                'horarios': horarios_creados
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
        from app import mysql
        
        horario = HorarioDisponible.obtener_por_id(mysql, horario_id)
        
        if not horario:
            return {
                'exito': False,
                'error': 'Horario no encontrado'
            }
        
        # Verificar si está ocupado
        esta_ocupado = HorarioDisponible.esta_ocupado(mysql, horario_id)
        
        return {
            'exito': True,
            'horario': {
                'id': horario['id'],
                'medico_id': horario['medico_id'],
                'medico_nombre': f"Dr. {horario['nombres']} {horario['apellidos']}",
                'especialidad': horario['especialidad'],
                'fecha': horario['fecha'].isoformat() if hasattr(horario['fecha'], 'isoformat') else str(horario['fecha']),
                'hora_inicio': horario['hora_inicio'].strftime('%H:%M') if hasattr(horario['hora_inicio'], 'strftime') else str(horario['hora_inicio']),
                'hora_fin': horario['hora_fin'].strftime('%H:%M') if hasattr(horario['hora_fin'], 'strftime') else str(horario['hora_fin']),
                'tipo': horario['tipo'],
                'consultorio': horario.get('consultorio') or 'Virtual',
                'duracion_cita': horario.get('duracion_cita', 60),
                'estado': horario['estado'],
                'observaciones': horario.get('observaciones') or '',
                'ocupado': esta_ocupado
            }
        }
        
    except Exception as e:
        print(f"Error en obtener_detalle_horario: {str(e)}")
        return {
            'exito': False,
            'error': f'Error al obtener horario: {str(e)}'
        }

def eliminar_horario_disponible(horario_id):
    """
    Elimina un horario disponible con validaciones de seguridad.
    """
    try:
        from app import mysql
        
        resultado = HorarioDisponible.eliminar_horario(mysql, horario_id)
        
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
        print(f"Error en eliminar_horario_disponible: {str(e)}")
        return {
            'exito': False,
            'error': f'Error al eliminar horario: {str(e)}'
        }

def obtener_estadisticas_horarios():
    """
    Retorna estadísticas resumidas del sistema de horarios.
    """
    try:
        from app import mysql
        cursor = mysql.connection.cursor()
        
        # Total de horarios activos
        cursor.execute("SELECT COUNT(*) as total FROM horarios_disponibles WHERE estado = 'ACTIVO'")
        total_horarios = cursor.fetchone()['total']
        
        # Contar ocupados vs disponibles
        cursor.execute("""
            SELECT COUNT(*) as ocupados 
            FROM horarios_disponibles h
            WHERE h.estado = 'ACTIVO' 
            AND EXISTS (
                SELECT 1 FROM citas c 
                WHERE c.horario_id = h.id AND c.estado = 'AGENDADA'
            )
        """)
        horarios_ocupados = cursor.fetchone()['ocupados']
        horarios_disponibles = total_horarios - horarios_ocupados
        
        # Estadísticas por tipo
        cursor.execute("""
            SELECT tipo, COUNT(*) as count 
            FROM horarios_disponibles 
            WHERE estado = 'ACTIVO'
            GROUP BY tipo
        """)
        stats_tipo = {row['tipo']: row['count'] for row in cursor.fetchall()}
        
        # Estadísticas por médico (top 5)
        cursor.execute("""
            SELECT CONCAT('Dr. ', p.nombres, ' ', p.apellidos) as medico_nombre, COUNT(*) as count
            FROM horarios_disponibles h
            JOIN profesionales p ON h.medico_id = p.id
            WHERE h.estado = 'ACTIVO'
            GROUP BY h.medico_id, p.nombres, p.apellidos
            ORDER BY count DESC
            LIMIT 5
        """)
        stats_medico_result = cursor.fetchall()
        stats_medico_ordenado = {row['medico_nombre']: row['count'] for row in stats_medico_result}
        
        cursor.close()
        
        return {
            'total_horarios': total_horarios,
            'horarios_ocupados': horarios_ocupados,
            'horarios_disponibles': horarios_disponibles,
            'por_tipo': stats_tipo,
            'por_medico': stats_medico_ordenado
        }
        
    except Exception as e:
        print(f"Error en obtener_estadisticas_horarios: {str(e)}")
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
        from app import mysql
        
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
        horario_existente = HorarioDisponible.obtener_por_id(mysql, horario_id)
        if not horario_existente:
            return {
                'exito': False,
                'error': 'El horario no existe'
            }

        # Validar que el profesional existe y está activo
        profesional = Profesional.obtener_por_id(mysql, datos_horario['medico_id'])
        
        if not profesional or profesional.get('estado') != 'ACTIVO':
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
                'error': 'No se pueden programar horarios en fechas pasadas'
            }
        
        # Validar rango de horas
        if hora_fin <= hora_inicio:
            return {
                'exito': False,
                'error': 'La hora de fin debe ser posterior a la hora de inicio'
            }
        
        # Verificar conflictos de horarios (excluyendo el horario actual)
        tiene_conflicto = HorarioDisponible.verificar_conflicto_horario(
            mysql, datos_horario['medico_id'], fecha, hora_inicio, hora_fin, excluir_id=horario_id
        )
        
        if tiene_conflicto:
            return {
                'exito': False,
                'error': 'Conflicto de horarios: ya existe un horario en ese rango de tiempo'
            }
        
        # Verificar si tiene citas agendadas
        citas_existentes = Cita.obtener_citas_activas_por_horario(mysql, horario_id)
        
        if len(citas_existentes) > 0:
            # Si tiene citas, verificar que los cambios no afecten el horario base
            hora_inicio_original = horario_existente['hora_inicio']
            hora_fin_original = horario_existente['hora_fin']
            
            # Convertir a time si es necesario
            if isinstance(hora_inicio_original, str):
                hora_inicio_original = datetime.strptime(hora_inicio_original, '%H:%M').time()
            if isinstance(hora_fin_original, str):
                hora_fin_original = datetime.strptime(hora_fin_original, '%H:%M').time()
            
            if hora_inicio > hora_inicio_original or hora_fin < hora_fin_original:
                return {
                    'exito': False,
                    'error': f'No se puede reducir el horario porque tiene {len(citas_existentes)} cita(s) agendada(s). Solo se puede extender.'
                }
        
        # Actualizar el horario
        resultado = HorarioDisponible.actualizar_horario(mysql, horario_id, datos_horario)
        
        if resultado:
            horario_actualizado = HorarioDisponible.obtener_por_id(mysql, horario_id)
            
            return {
                'exito': True,
                'mensaje': 'Horario actualizado exitosamente',
                'horario': {
                    'id': horario_actualizado['id'],
                    'medico_nombre': f"Dr. {horario_actualizado['nombres']} {horario_actualizado['apellidos']}",
                    'fecha': horario_actualizado['fecha'].isoformat() if hasattr(horario_actualizado['fecha'], 'isoformat') else str(horario_actualizado['fecha']),
                    'hora_inicio': horario_actualizado['hora_inicio'].strftime('%H:%M') if hasattr(horario_actualizado['hora_inicio'], 'strftime') else str(horario_actualizado['hora_inicio']),
                    'hora_fin': horario_actualizado['hora_fin'].strftime('%H:%M') if hasattr(horario_actualizado['hora_fin'], 'strftime') else str(horario_actualizado['hora_fin']),
                    'tipo': horario_actualizado['tipo'],
                    'consultorio': horario_actualizado.get('consultorio')
                }
            }
        else:
            return {
                'exito': False,
                'error': 'Error al actualizar el horario'
            }
        
    except Exception as e:
        print(f"Error en actualizar_horario_disponible: {str(e)}")
        return {
            'exito': False,
            'error': f'Error interno: {str(e)}'
        }