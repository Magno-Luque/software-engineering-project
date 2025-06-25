# models/admin_dashboard.py

from datetime import date

class ResumenDashboard:
    """Modelo para la tabla resumen_dashboard usando Flask-MySQLdb"""
    
    def __init__(self, mysql):
        self.mysql = mysql
    
    @classmethod
    def obtener_resumen(cls, mysql):
        """
        Retorna el resumen de métricas del dashboard.
        
        Returns:
            dict: Diccionario con métricas actualizadas
            
        Notas:
            - Calcula las métricas en tiempo real para mayor precisión
            - Mantiene compatibilidad con el formato esperado por el frontend
        """
        try:
            cursor = mysql.connection.cursor()
            
            # Obtener total de pacientes activos
            cursor.execute("SELECT COUNT(*) as total FROM pacientes WHERE estado = 'ACTIVO'")
            total_pacientes = cursor.fetchone()['total']
            
            # Obtener total de profesionales activos
            cursor.execute("SELECT COUNT(*) as total FROM profesionales WHERE estado = 'ACTIVO'")
            total_profesionales = cursor.fetchone()['total']
            
            # Obtener citas de hoy
            hoy = date.today()
            cursor.execute("SELECT COUNT(*) as total FROM citas WHERE fecha_cita = %s", (hoy,))
            citas_hoy = cursor.fetchone()['total']
            
            # Obtener alertas críticas activas
            cursor.execute("SELECT COUNT(*) as total FROM alertas_criticas WHERE estado = 'PENDIENTE'")
            alertas_criticas = cursor.fetchone()['total']
            
            cursor.close()
            
            return {
                'total_pacientes': total_pacientes,
                'total_profesionales': total_profesionales,
                'total_citas_hoy': citas_hoy,
                'total_alertas_criticas': alertas_criticas
            }
            
        except Exception as e:
            print(f"Error al obtener resumen del dashboard: {str(e)}")
            return {
                'total_pacientes': 0,
                'total_profesionales': 0,
                'total_citas_hoy': 0,
                'total_alertas_criticas': 0
            }
    
    @classmethod
    def actualizar_resumen_tabla(cls, mysql):
        """
        Actualiza el registro en la tabla resumen_dashboard.
        
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
            
        Notas:
            - Mantiene la tabla resumen_dashboard para compatibilidad
            - Actualiza o inserta según sea necesario
        """
        try:
            cursor = mysql.connection.cursor()
            
            # Calcular métricas actuales
            resumen = cls.obtener_resumen(mysql)
            
            # Verificar si existe un registro
            cursor.execute("SELECT COUNT(*) as total FROM resumen_dashboard")
            existe = cursor.fetchone()['total'] > 0
            
            if existe:
                # Actualizar registro existente
                query = """
                    UPDATE resumen_dashboard 
                    SET total_pacientes = %s, 
                        total_profesionales = %s, 
                        citas_hoy = %s, 
                        alertas_criticas_activas = %s,
                        fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE id = (SELECT MIN(id) FROM resumen_dashboard)
                """
            else:
                # Insertar nuevo registro
                query = """
                    INSERT INTO resumen_dashboard 
                    (total_pacientes, total_profesionales, citas_hoy, alertas_criticas_activas)
                    VALUES (%s, %s, %s, %s)
                """
            
            cursor.execute(query, (
                resumen['total_pacientes'],
                resumen['total_profesionales'],
                resumen['total_citas_hoy'],
                resumen['total_alertas_criticas']
            ))
            
            mysql.connection.commit()
            cursor.close()
            
            print("Resumen del dashboard actualizado exitosamente")
            return True
            
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al actualizar resumen del dashboard: {str(e)}")
            return False
    
    @classmethod
    def obtener_resumen_desde_tabla(cls, mysql):
        """
        Obtiene el resumen desde la tabla resumen_dashboard (datos precalculados).
        
        Returns:
            dict: Diccionario con métricas desde la tabla
            
        Notas:
            - Más rápido que calcular en tiempo real
            - Requiere que la tabla esté actualizada
        """
        try:
            cursor = mysql.connection.cursor()
            
            query = """
                SELECT total_pacientes, total_profesionales, citas_hoy, 
                       alertas_criticas_activas, fecha_actualizacion
                FROM resumen_dashboard 
                ORDER BY id DESC 
                LIMIT 1
            """
            
            cursor.execute(query)
            resumen = cursor.fetchone()
            cursor.close()
            
            if resumen:
                return {
                    'total_pacientes': resumen['total_pacientes'],
                    'total_profesionales': resumen['total_profesionales'],
                    'total_citas_hoy': resumen['citas_hoy'],
                    'total_alertas_criticas': resumen['alertas_criticas_activas'],
                    'fecha_actualizacion': resumen['fecha_actualizacion']
                }
            else:
                # Si no hay datos, retornar métricas en tiempo real
                return cls.obtener_resumen(mysql)
                
        except Exception as e:
            print(f"Error al obtener resumen desde tabla: {str(e)}")
            return cls.obtener_resumen(mysql)
    
    @classmethod
    def obtener_estadisticas_detalladas(cls, mysql):
        """
        Obtiene estadísticas más detalladas para el dashboard.
        
        Returns:
            dict: Diccionario con estadísticas detalladas
        """
        try:
            cursor = mysql.connection.cursor()
            
            # Estadísticas de citas por estado
            cursor.execute("""
                SELECT estado, COUNT(*) as cantidad
                FROM citas 
                WHERE fecha_cita >= CURDATE() - INTERVAL 30 DAY
                GROUP BY estado
            """)
            citas_por_estado = cursor.fetchall()
            
            # Estadísticas de profesionales por especialidad
            cursor.execute("""
                SELECT especialidad, COUNT(*) as cantidad
                FROM profesionales 
                WHERE estado = 'ACTIVO'
                GROUP BY especialidad
            """)
            profesionales_por_especialidad = cursor.fetchall()
            
            # Citas por día (últimos 7 días)
            cursor.execute("""
                SELECT DATE(fecha_cita) as fecha, COUNT(*) as cantidad
                FROM citas 
                WHERE fecha_cita >= CURDATE() - INTERVAL 7 DAY
                GROUP BY DATE(fecha_cita)
                ORDER BY fecha
            """)
            citas_por_dia = cursor.fetchall()
            
            # Alertas críticas por tipo
            cursor.execute("""
                SELECT tipo_alerta, COUNT(*) as cantidad
                FROM alertas_criticas 
                WHERE estado = 'PENDIENTE'
                GROUP BY tipo_alerta
            """)
            alertas_por_tipo = cursor.fetchall()
            
            cursor.close()
            
            return {
                'citas_por_estado': citas_por_estado,
                'profesionales_por_especialidad': profesionales_por_especialidad,
                'citas_por_dia': citas_por_dia,
                'alertas_por_tipo': alertas_por_tipo
            }
            
        except Exception as e:
            print(f"Error al obtener estadísticas detalladas: {str(e)}")
            return {
                'citas_por_estado': [],
                'profesionales_por_especialidad': [],
                'citas_por_dia': [],
                'alertas_por_tipo': []
            }
    
    @classmethod
    def obtener_actividad_reciente(cls, mysql, limit=10):
        """
        Obtiene la actividad reciente del sistema.
        
        Args:
            limit (int): Número máximo de registros a retornar
            
        Returns:
            list: Lista de actividades recientes
        """
        try:
            cursor = mysql.connection.cursor()
            
            # Citas recientes
            cursor.execute("""
                SELECT 'cita' as tipo, c.id, c.fecha_creacion,
                       CONCAT(p.nombres, ' ', p.apellidos) as paciente,
                       CONCAT(pr.nombres, ' ', pr.apellidos) as profesional,
                       c.estado
                FROM citas c
                JOIN pacientes p ON c.paciente_id = p.id
                JOIN profesionales pr ON c.medico_id = pr.id
                ORDER BY c.fecha_creacion DESC
                LIMIT %s
            """, (limit // 2,))
            
            citas_recientes = cursor.fetchall()
            
            # Pacientes recientes
            cursor.execute("""
                SELECT 'paciente' as tipo, id, fecha_registro as fecha_creacion,
                       CONCAT(nombres, ' ', apellidos) as nombre,
                       estado
                FROM pacientes
                ORDER BY fecha_registro DESC
                LIMIT %s
            """, (limit // 2,))
            
            pacientes_recientes = cursor.fetchall()
            
            cursor.close()
            
            # Combinar y ordenar por fecha
            actividad = []
            
            for cita in citas_recientes:
                actividad.append({
                    'tipo': 'cita',
                    'id': cita['id'],
                    'fecha': cita['fecha_creacion'],
                    'descripcion': f"Cita agendada para {cita['paciente']} con {cita['profesional']}",
                    'estado': cita['estado']
                })
            
            for paciente in pacientes_recientes:
                actividad.append({
                    'tipo': 'paciente',
                    'id': paciente['id'],
                    'fecha': paciente['fecha_creacion'],
                    'descripcion': f"Nuevo paciente registrado: {paciente['nombre']}",
                    'estado': paciente['estado']
                })
            
            # Ordenar por fecha descendente
            actividad.sort(key=lambda x: x['fecha'], reverse=True)
            
            return actividad[:limit]
            
        except Exception as e:
            print(f"Error al obtener actividad reciente: {str(e)}")
            return []
    
    @classmethod
    def obtener_metricas_rendimiento(cls, mysql):
        """
        Obtiene métricas de rendimiento del sistema.
        
        Returns:
            dict: Diccionario con métricas de rendimiento
        """
        try:
            cursor = mysql.connection.cursor()
            
            # Promedio de citas por día
            cursor.execute("""
                SELECT AVG(citas_por_dia) as promedio
                FROM (
                    SELECT DATE(fecha_cita) as fecha, COUNT(*) as citas_por_dia
                    FROM citas 
                    WHERE fecha_cita >= CURDATE() - INTERVAL 30 DAY
                    GROUP BY DATE(fecha_cita)
                ) as subconsulta
            """)
            promedio_citas = cursor.fetchone()
            
            # Tasa de citas atendidas
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_citas,
                    SUM(CASE WHEN estado = 'ATENDIDA' THEN 1 ELSE 0 END) as citas_atendidas
                FROM citas 
                WHERE fecha_cita >= CURDATE() - INTERVAL 30 DAY
            """)
            tasa_atencion = cursor.fetchone()
            
            # Tiempo promedio de espera (días entre registro y primera cita)
            cursor.execute("""
                SELECT AVG(DATEDIFF(c.fecha_cita, p.fecha_registro)) as tiempo_espera_promedio
                FROM citas c
                JOIN pacientes p ON c.paciente_id = p.id
                WHERE c.fecha_cita >= CURDATE() - INTERVAL 30 DAY
            """)
            tiempo_espera = cursor.fetchone()
            
            cursor.close()
            
            # Calcular porcentaje de atención
            porcentaje_atencion = 0
            if tasa_atencion['total_citas'] > 0:
                porcentaje_atencion = (tasa_atencion['citas_atendidas'] / tasa_atencion['total_citas']) * 100
            
            return {
                'promedio_citas_dia': round(promedio_citas['promedio'] or 0, 2),
                'porcentaje_atencion': round(porcentaje_atencion, 2),
                'tiempo_espera_promedio': round(tiempo_espera['tiempo_espera_promedio'] or 0, 1),
                'total_citas_mes': tasa_atencion['total_citas'],
                'citas_atendidas_mes': tasa_atencion['citas_atendidas']
            }
            
        except Exception as e:
            print(f"Error al obtener métricas de rendimiento: {str(e)}")
            return {
                'promedio_citas_dia': 0,
                'porcentaje_atencion': 0,
                'tiempo_espera_promedio': 0,
                'total_citas_mes': 0,
                'citas_atendidas_mes': 0
            }