// static/js/desktop/medico-alertas.js
document.addEventListener('DOMContentLoaded', () => {
    console.log('Módulo de alertas críticas cargado.');
    
    // Inicializar funcionalidades
    inicializarMonitoreoTiempoReal();
    actualizarTimestamp();
    
    // Actualizar cada 30 segundos
    setInterval(actualizarTimestamp, 30000);
    setInterval(verificarNuevasAlertas, 30000);
    
    // Configurar fecha de hoy en filtros
    const hoy = new Date().toISOString().split('T')[0];
    document.getElementById('filtro-fecha-desde').value = hoy;
    document.getElementById('filtro-fecha-hasta').value = hoy;
});

function inicializarMonitoreoTiempoReal() {
    const statusIndicator = document.getElementById('status-indicator');
    
    // Animación del indicador de estado
    setInterval(() => {
        const circle = statusIndicator.querySelector('i');
        circle.style.color = circle.style.color === 'rgb(40, 167, 69)' ? '#28a745' : '#28a745';
    }, 2000);
    
    console.log('Monitoreo en tiempo real activo');
}

function actualizarTimestamp() {
    const now = new Date();
    const timestamp = now.toLocaleTimeString('es-PE', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    document.getElementById('timestamp').textContent = timestamp;
}

function verificarNuevasAlertas() {
    // Simular verificación de nuevas alertas
    // En producción esto sería una llamada WebSocket o API
    
    if (Math.random() < 0.1) { // 10% probabilidad
        mostrarNuevaAlerta();
    }
}

function mostrarNuevaAlerta() {
    // Incrementar contador
    const badge = document.getElementById('alertas-count');
    const currentCount = parseInt(badge.textContent);
    badge.textContent = currentCount + 1;
    
    // Incrementar contador de críticas
    const countCriticas = document.getElementById('count-criticas');
    const currentCriticas = parseInt(countCriticas.textContent);
    countCriticas.textContent = currentCriticas + 1;
    
    // Mostrar notificación
    mostrarNotificacionNuevaAlerta();
    
    console.log('Nueva alerta crítica detectada');
}

function mostrarNotificacionNuevaAlerta() {
    // Crear notificación flotante
    const notification = document.createElement('div');
    notification.className = 'alerta-notification';
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: linear-gradient(135deg, #dc3545, #c82333);
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(220, 53, 69, 0.4);
        z-index: 1001;
        animation: alertSlideIn 0.5s ease;
        min-width: 300px;
    `;
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-exclamation-triangle" style="font-size: 20px; animation: alertPulse 1s infinite;"></i>
            <div>
                <strong>¡NUEVA ALERTA CRÍTICA!</strong><br>
                <small>Un paciente requiere atención inmediata</small>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" 
                    style="background: none; border: none; color: white; font-size: 18px; cursor: pointer;">×</button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Reproducir sonido de alerta
    reproducirSonidoAlerta();
    
    // Auto-remover después de 8 segundos
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 8000);
}

function reproducirSonidoAlerta() {
    try {
        // Crear beep con AudioContext
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
    } catch (e) {
        console.log('Audio no disponible');
    }
}

function aplicarFiltrosAlertas() {
    const tipoFiltro = document.getElementById('filtro-tipo').value;
    const pacienteFiltro = document.getElementById('filtro-paciente').value;
    const fechaDesde = document.getElementById('filtro-fecha-desde').value;
    const fechaHasta = document.getElementById('filtro-fecha-hasta').value;
    
    console.log('Aplicando filtros:', { tipoFiltro, pacienteFiltro, fechaDesde, fechaHasta });
    
    const alertas = document.querySelectorAll('.alerta-item');
    let alertasVisibles = 0;
    
    alertas.forEach(alerta => {
        let mostrar = true;
        
        // Filtro por tipo
        if (tipoFiltro !== 'todas') {
            const tipoAlerta = alerta.getAttribute('data-tipo');
            if (tipoAlerta !== tipoFiltro) {
                mostrar = false;
            }
        }
        
        // Filtro por paciente
        if (pacienteFiltro !== 'todos') {
            const pacienteAlerta = alerta.getAttribute('data-paciente');
            if (pacienteAlerta !== pacienteFiltro) {
                mostrar = false;
            }
        }
        
        // Aplicar filtro de fecha aquí si es necesario
        
        alerta.style.display = mostrar ? 'block' : 'none';
        if (mostrar) alertasVisibles++;
    });
    
    // Mostrar mensaje si no hay resultados
    mostrarResultadosFiltro(alertasVisibles);
}

function mostrarResultadosFiltro(cantidad) {
    // Remover mensaje previo si existe
    const mensajePrevio = document.getElementById('mensaje-filtros');
    if (mensajePrevio) {
        mensajePrevio.remove();
    }
    
    if (cantidad === 0) {
        const mensaje = document.createElement('div');
        mensaje.id = 'mensaje-filtros';
        mensaje.className = 'mensaje-sin-resultados';
        mensaje.style.cssText = `
            text-align: center;
            padding: 40px;
            color: var(--text-gray);
            background: var(--card-bg);
            border-radius: 8px;
            margin: 20px 0;
        `;
        mensaje.innerHTML = `
            <i class="fas fa-filter" style="font-size: 48px; opacity: 0.3; margin-bottom: 15px;"></i><br>
            <strong>No se encontraron alertas</strong><br>
            <small>Intente modificar los filtros de búsqueda</small>
        `;
        
        document.getElementById('lista-alertas').appendChild(mensaje);
    }
}

function contactarPaciente(alertaId, nombrePaciente) {
    console.log(`Contactando a paciente: ${nombrePaciente} (ID: ${alertaId})`);
    
    if (confirm(`¿Desea contactar a ${nombrePaciente}?`)) {
        // Simular llamada
        const alerta = document.querySelector(`[data-id="${alertaId}"]`);
        const tiempoElement = alerta.querySelector('.alerta-tiempo span');
        
        // Marcar como contactado
        tiempoElement.innerHTML = `Contactado <i class="fas fa-phone-alt" style="color: var(--positive-change);"></i>`;
        
        // Mostrar modal de seguimiento
        mostrarModalSeguimiento(alertaId, nombrePaciente);
        
        console.log(`Contacto iniciado con ${nombrePaciente}`);
    }
}

function mostrarModalSeguimiento(alertaId, nombrePaciente) {
    const seguimiento = prompt(`Resultado del contacto con ${nombrePaciente}:`);
    
    if (seguimiento && seguimiento.trim()) {
        // Agregar nota de seguimiento a la alerta
        const alerta = document.querySelector(`[data-id="${alertaId}"]`);
        const contexto = alerta.querySelector('.alerta-contexto');
        
        const notaSeguimiento = document.createElement('div');
        notaSeguimiento.className = 'nota-seguimiento';
        notaSeguimiento.style.cssText = `
            background: #e8f5e8;
            border-left: 3px solid var(--positive-change);
            padding: 8px 12px;
            margin-top: 8px;
            border-radius: 4px;
            font-size: 0.9em;
        `;
        notaSeguimiento.innerHTML = `
            <strong>Seguimiento:</strong> ${seguimiento}<br>
            <small style="color: var(--text-gray);">${new Date().toLocaleString('es-PE')}</small>
        `;
        
        contexto.appendChild(notaSeguimiento);
    }
}

function derivarEmergencia(alertaId) {
    const alerta = document.querySelector(`[data-id="${alertaId}"]`);
    const nombrePaciente = alerta.querySelector('.paciente-info strong').textContent;
    
    if (confirm(`¿Derivar a ${nombrePaciente} al servicio de emergencia?\n\nEsta acción notificará inmediatamente al equipo de emergencias.`)) {
        // Marcar alerta como derivada
        alerta.style.background = '#fff3cd';
        alerta.style.borderLeft = '4px solid #ffc107';
        
        // Cambiar el tipo de urgencia
        const urgencia = alerta.querySelector('.alerta-urgencia');
        urgencia.innerHTML = '<i class="fas fa-ambulance"></i><span>DERIVADO</span>';
        urgencia.style.background = '#ffc107';
        
        // Deshabilitar otros botones
        const botones = alerta.querySelectorAll('.btn-accion');
        botones.forEach(btn => {
            if (!btn.classList.contains('notas')) {
                btn.disabled = true;
                btn.style.opacity = '0.5';
            }
        });
        
        // Simular notificación a emergencias
        mostrarNotificacionEmergencia(nombrePaciente);
        
        console.log(`${nombrePaciente} derivado a emergencias`);
    }
}

function mostrarNotificacionEmergencia(nombrePaciente) {
    const notification = document.createElement('div');
    notification.className = 'emergencia-notification';
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: linear-gradient(135deg, #ffc107, #e0a800);
        color: #212529;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(255, 193, 7, 0.4);
        z-index: 1001;
        animation: alertSlideIn 0.5s ease;
        min-width: 320px;
    `;
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-ambulance" style="font-size: 20px; animation: alertPulse 1s infinite;"></i>
            <div>
                <strong>DERIVACIÓN A EMERGENCIAS</strong><br>
                <small>${nombrePaciente} - Notificación enviada</small>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" 
                    style="background: none; border: none; color: #212529; font-size: 18px; cursor: pointer;">×</button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 10000);
}

function resolverAlerta(alertaId) {
    const alerta = document.querySelector(`[data-id="${alertaId}"]`);
    const nombrePaciente = alerta.querySelector('.paciente-info strong').textContent;
    const tipoAlerta = alerta.querySelector('.alerta-tipo strong').textContent;
    
    // Mostrar modal de resolución
    document.getElementById('modal-resolver').style.display = 'flex';
    
    // Llenar detalles en el modal
    document.getElementById('alerta-detalle-modal').innerHTML = `
        <div style="background: var(--light-blue); padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <strong>Paciente:</strong> ${nombrePaciente}<br>
            <strong>Tipo de Alerta:</strong> ${tipoAlerta}<br>
            <strong>ID:</strong> ${alertaId}
        </div>
    `;
    
    // Guardar ID para usar en confirmación
    document.getElementById('modal-resolver').setAttribute('data-alerta-id', alertaId);
}

function confirmarResolucion() {
    const alertaId = document.getElementById('modal-resolver').getAttribute('data-alerta-id');
    const accionesTomadas = document.getElementById('acciones-tomadas').value;
    const estadoPaciente = document.getElementById('estado-paciente').value;
    const notificarCuidador = document.getElementById('notificar-cuidador').checked;
    const programarSeguimiento = document.getElementById('programar-seguimiento').checked;
    
    if (!accionesTomadas.trim()) {
        alert('Por favor, describa las acciones tomadas.');
        return;
    }
    
    // Marcar alerta como resuelta
    const alerta = document.querySelector(`[data-id="${alertaId}"]`);
    alerta.style.background = '#d4edda';
    alerta.style.borderLeft = '4px solid var(--positive-change)';
    alerta.style.opacity = '0.8';
    
    // Cambiar urgencia a resuelto
    const urgencia = alerta.querySelector('.alerta-urgencia');
    urgencia.innerHTML = '<i class="fas fa-check-circle"></i><span>RESUELTO</span>';
    urgencia.style.background = 'var(--positive-change)';
    
    // Deshabilitar botones
    const botones = alerta.querySelectorAll('.btn-accion');
    botones.forEach(btn => {
        btn.disabled = true;
        btn.style.opacity = '0.5';
    });
    
    // Agregar nota de resolución
    const contexto = alerta.querySelector('.alerta-contexto');
    const notaResolucion = document.createElement('div');
    notaResolucion.className = 'nota-resolucion';
    notaResolucion.style.cssText = `
        background: #d4edda;
        border-left: 3px solid var(--positive-change);
        padding: 10px;
        margin-top: 10px;
        border-radius: 4px;
    `;
    notaResolucion.innerHTML = `
        <strong>Resolución:</strong> ${accionesTomadas}<br>
        <strong>Estado:</strong> ${estadoPaciente}<br>
        <small style="color: var(--text-gray);">Resuelto el ${new Date().toLocaleString('es-PE')}</small>
    `;
    
    contexto.appendChild(notaResolucion);
    
    // Actualizar contadores
    actualizarContadores();
    
    // Cerrar modal
    cerrarModalResolver();
    
    // Mover a historial después de 3 segundos
    setTimeout(() => {
        moverAHistorial(alerta);
    }, 3000);
    
    console.log(`Alerta ${alertaId} resuelta`);
}

function actualizarContadores() {
    // Contar alertas visibles por tipo
    const criticas = document.querySelectorAll('.alerta-item.critica[style*="display: block"], .alerta-item.critica:not([style])').length;
    const medias = document.querySelectorAll('.alerta-item.media[style*="display: block"], .alerta-item.media:not([style])').length;
    const bajas = document.querySelectorAll('.alerta-item.baja[style*="display: block"], .alerta-item.baja:not([style])').length;
    
    // Contar resueltas (background verde)
    const resueltas = document.querySelectorAll('.alerta-item[style*="background: rgb(212, 237, 218)"]').length;
    
    document.getElementById('count-criticas').textContent = Math.max(0, criticas - resueltas);
    document.getElementById('count-medias').textContent = Math.max(0, medias);
    document.getElementById('count-bajas').textContent = Math.max(0, bajas);
    document.getElementById('count-resueltas').textContent = parseInt(document.getElementById('count-resueltas').textContent) + 1;
    
    // Actualizar badge
    const totalPendientes = Math.max(0, criticas + medias + bajas - resueltas);
    document.getElementById('alertas-count').textContent = totalPendientes;
}

function moverAHistorial(alertaElement) {
    // Crear elemento para historial
    const nombrePaciente = alertaElement.querySelector('.paciente-info strong').textContent;
    const tipoAlerta = alertaElement.querySelector('.alerta-tipo strong').textContent;
    const valor = alertaElement.querySelector('.valor-critico, .medicamento-omitido, .cita-perdida').textContent;
    
    const historialItem = document.createElement('div');
    historialItem.className = 'alerta-resuelta';
    historialItem.innerHTML = `
        <div class="resuelta-info">
            <strong>${nombrePaciente}</strong> - ${tipoAlerta} (${valor})
        </div>
        <div class="resuelta-tiempo">
            Resuelto: ${new Date().toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })} | Tratado por médico
        </div>
    `;
    
    // Agregar al historial
    const historialContenido = document.getElementById('historial-contenido');
    historialContenido.insertBefore(historialItem, historialContenido.firstChild);
    
    // Ocultar alerta original con animación
    alertaElement.style.transition = 'opacity 1s ease, transform 1s ease';
    alertaElement.style.opacity = '0';
    alertaElement.style.transform = 'translateX(-100%)';
    
    setTimeout(() => {
        alertaElement.remove();
    }, 1000);
}

function agregarNotaAlerta(alertaId) {
    const nota = prompt('Agregar nota a la alerta:');
    
    if (nota && nota.trim()) {
        const alerta = document.querySelector(`[data-id="${alertaId}"]`);
        const contexto = alerta.querySelector('.alerta-contexto');
        
        const notaElement = document.createElement('div');
        notaElement.className = 'nota-medica';
        notaElement.style.cssText = `
            background: #f8f9fa;
            border-left: 3px solid var(--secondary-blue);
            padding: 8px 12px;
            margin-top: 8px;
            border-radius: 4px;
            font-size: 0.9em;
        `;
        notaElement.innerHTML = `
            <strong>Nota:</strong> ${nota}<br>
            <small style="color: var(--text-gray);">${new Date().toLocaleString('es-PE')}</small>
        `;
        
        contexto.appendChild(notaElement);
        
        console.log(`Nota agregada a alerta ${alertaId}: ${nota}`);
    }
}

function enviarRecordatorio(alertaId) {
    const alerta = document.querySelector(`[data-id="${alertaId}"]`);
    const nombrePaciente = alerta.querySelector('.paciente-info strong').textContent;
    
    if (confirm(`¿Enviar recordatorio de medicación a ${nombrePaciente}?`)) {
        // Simular envío de recordatorio
        const tiempo = alerta.querySelector('.alerta-tiempo span');
        tiempo.innerHTML = `Recordatorio enviado <i class="fas fa-bell" style="color: var(--medium-criticality);"></i>`;
        
        // Agregar nota de recordatorio
        agregarNotaAutomatica(alertaId, 'Recordatorio de medicación enviado al paciente');
        
        alert('Recordatorio enviado correctamente al paciente.');
        console.log(`Recordatorio enviado a ${nombrePaciente}`);
    }
}

function reprogramarCita(alertaId) {
    const alerta = document.querySelector(`[data-id="${alertaId}"]`);
    const nombrePaciente = alerta.querySelector('.paciente-info strong').textContent;
    
    if (confirm(`¿Reprogramar cita para ${nombrePaciente}?`)) {
        // En una aplicación real, esto redirigiría al calendario
        alert(`Redirigiendo al calendario para reprogramar cita de ${nombrePaciente}...`);
        
        // Simular reprogramación
        agregarNotaAutomatica(alertaId, 'Cita reprogramada - Pendiente confirmación del paciente');
        
        console.log(`Reprogramando cita para ${nombrePaciente}`);
    }
}

function agregarNotaAutomatica(alertaId, mensaje) {
    const alerta = document.querySelector(`[data-id="${alertaId}"]`);
    const contexto = alerta.querySelector('.alerta-contexto');
    
    const notaAuto = document.createElement('div');
    notaAuto.className = 'nota-automatica';
    notaAuto.style.cssText = `
        background: #e7f3ff;
        border-left: 3px solid var(--secondary-blue);
        padding: 8px 12px;
        margin-top: 8px;
        border-radius: 4px;
        font-size: 0.9em;
    `;
    notaAuto.innerHTML = `
        <strong>Sistema:</strong> ${mensaje}<br>
        <small style="color: var(--text-gray);">${new Date().toLocaleString('es-PE')}</small>
    `;
    
    contexto.appendChild(notaAuto);
}

function refrescarAlertas() {
    console.log('Refrescando alertas...');
    
    // Simular carga
    const botonRefrescar = document.querySelector('.btn-refrescar');
    const iconoOriginal = botonRefrescar.innerHTML;
    
    botonRefrescar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refrescando...';
    botonRefrescar.disabled = true;
    
    setTimeout(() => {
        botonRefrescar.innerHTML = iconoOriginal;
        botonRefrescar.disabled = false;
        actualizarTimestamp();
        
        // Simular nueva alerta ocasionalmente
        if (Math.random() < 0.3) {
            mostrarNuevaAlerta();
        }
        
        console.log('Alertas refrescadas');
    }, 2000);
}

function resolverTodasAlertas() {
    const alertasPendientes = document.querySelectorAll('.alerta-item:not([style*="background: rgb(212, 237, 218)"])');
    
    if (alertasPendientes.length === 0) {
        alert('No hay alertas pendientes para resolver.');
        return;
    }
    
    if (confirm(`¿Resolver todas las ${alertasPendientes.length} alertas pendientes?\n\nEsta acción marcará todas las alertas como resueltas.`)) {
        alertasPendientes.forEach((alerta, index) => {
            setTimeout(() => {
                const alertaId = alerta.getAttribute('data-id');
                
                // Simular resolución automática
                alerta.style.background = '#d4edda';
                alerta.style.borderLeft = '4px solid var(--positive-change)';
                alerta.style.opacity = '0.8';
                
                const urgencia = alerta.querySelector('.alerta-urgencia');
                urgencia.innerHTML = '<i class="fas fa-check-circle"></i><span>RESUELTO</span>';
                urgencia.style.background = 'var(--positive-change)';
                
                // Deshabilitar botones
                const botones = alerta.querySelectorAll('.btn-accion');
                botones.forEach(btn => {
                    btn.disabled = true;
                    btn.style.opacity = '0.5';
                });
                
                // Mover a historial después de un tiempo
                setTimeout(() => {
                    moverAHistorial(alerta);
                }, 2000);
                
            }, index * 500); // Escalonar las resoluciones
        });
        
        // Actualizar contadores después de procesar todas
        setTimeout(() => {
            document.getElementById('count-criticas').textContent = '0';
            document.getElementById('count-medias').textContent = '0';
            document.getElementById('count-bajas').textContent = '0';
            document.getElementById('alertas-count').textContent = '0';
        }, alertasPendientes.length * 500 + 1000);
    }
}

function exportarAlertas() {
    console.log('Exportando alertas a PDF...');
    
    const botonExportar = document.querySelector('.btn-exportar');
    const textoOriginal = botonExportar.innerHTML;
    
    botonExportar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generando PDF...';
    botonExportar.disabled = true;
    
    setTimeout(() => {
        botonExportar.innerHTML = textoOriginal;
        botonExportar.disabled = false;
        
        alert('Reporte de alertas exportado correctamente.\n\nEl archivo incluye:\n• Alertas pendientes y resueltas\n• Estadísticas del período\n• Acciones tomadas\n• Tiempos de respuesta');
        
        console.log('Exportación completada');
    }, 3000);
}

function toggleHistorial() {
    const historial = document.getElementById('historial-contenido');
    const boton = document.querySelector('.btn-toggle i');
    
    if (historial.style.display === 'none') {
        historial.style.display = 'block';
        boton.className = 'fas fa-chevron-up';
    } else {
        historial.style.display = 'none';
        boton.className = 'fas fa-chevron-down';
    }
}

function cerrarModalResolver() {
    document.getElementById('modal-resolver').style.display = 'none';
    
    // Limpiar formulario
    document.getElementById('acciones-tomadas').value = '';
    document.getElementById('estado-paciente').value = 'estable';
    document.getElementById('notificar-cuidador').checked = false;
    document.getElementById('programar-seguimiento').checked = false;
}

// Cerrar modal con ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        cerrarModalResolver();
    }
});

// Agregar animaciones CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes alertSlideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes alertPulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
`;
document.head.appendChild(style);