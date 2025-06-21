// static/js/desktop/medico-consultas.js
document.addEventListener('DOMContentLoaded', () => {
    console.log('Módulo de consultas virtuales cargado.');
    
    // Inicializar funcionalidades
    inicializarConsultas();
    configurarFechaHoy();
    verificarEstadoZoom();
    
    // Verificar consultas próximas cada 5 minutos
    setInterval(verificarConsultasProximas, 5 * 60 * 1000);
});

function inicializarConsultas() {
    // Actualizar tiempo real para consultas en curso
    actualizarTiemposReales();
    setInterval(actualizarTiemposReales, 60000); // Cada minuto
    
    console.log('Sistema de consultas inicializado');
}

function configurarFechaHoy() {
    const hoy = new Date().toISOString().split('T')[0];
    document.getElementById('filtro-fecha').value = hoy;
}

function verificarEstadoZoom() {
    const statusElement = document.getElementById('zoom-status');
    
    // Simular verificación de conexión Zoom
    setTimeout(() => {
        const conectado = Math.random() > 0.1; // 90% probabilidad de estar conectado
        
        if (conectado) {
            statusElement.innerHTML = '<i class="fas fa-video" style="color: var(--positive-change);"></i> Zoom Conectado';
            statusElement.style.color = 'var(--positive-change)';
        } else {
            statusElement.innerHTML = '<i class="fas fa-exclamation-triangle" style="color: var(--high-criticality);"></i> Error de Conexión';
            statusElement.style.color = 'var(--high-criticality)';
            mostrarAlertaConexion();
        }
    }, 2000);
}

function mostrarAlertaConexion() {
    const alerta = document.createElement('div');
    alerta.className = 'conexion-alerta';
    alerta.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: var(--high-criticality);
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(220, 53, 69, 0.4);
        z-index: 1001;
        animation: slideIn 0.5s ease;
    `;
    
    alerta.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-exclamation-triangle"></i>
            <div>
                <strong>Error de Conexión Zoom</strong><br>
                <small>Verificar configuración de red</small>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" 
                    style="background: none; border: none; color: white; font-size: 18px; cursor: pointer;">×</button>
        </div>
    `;
    
    document.body.appendChild(alerta);
    
    setTimeout(() => {
        if (alerta.parentElement) {
            alerta.remove();
        }
    }, 8000);
}

function actualizarTiemposReales() {
    const ahora = new Date();
    const horaActual = ahora.getHours();
    const minutoActual = ahora.getMinutes();
    
    // Verificar consultas que deberían estar en curso
    const consultas = document.querySelectorAll('.consulta-card');
    
    consultas.forEach(consulta => {
        const horaElemento = consulta.querySelector('.hora');
        if (!horaElemento) return;
        
        const horaConsulta = horaElemento.textContent.split(':');
        const horaInicio = parseInt(horaConsulta[0]);
        const minutoInicio = parseInt(horaConsulta[1]);
        
        const tiempoTranscurrido = (horaActual * 60 + minutoActual) - (horaInicio * 60 + minutoInicio);
        
        if (tiempoTranscurrido >= 0 && tiempoTranscurrido <= 45) {
            // Consulta en curso
            marcarConsultaEnCurso(consulta, tiempoTranscurrido);
        } else if (tiempoTranscurrido < -15) {
            // Consulta próxima (menos de 15 minutos)
            marcarConsultaProxima(consulta, Math.abs(tiempoTranscurrido));
        }
    });
}

function marcarConsultaEnCurso(consulta, minutos) {
    const statusIndicator = consulta.querySelector('.status-indicator');
    if (statusIndicator && !statusIndicator.classList.contains('en-curso')) {
        statusIndicator.className = 'status-indicator en-curso';
        statusIndicator.innerHTML = '<i class="fas fa-play-circle"></i><span>EN CURSO</span>';
        
        // Agregar tiempo transcurrido
        const tiempoElement = consulta.querySelector('.consulta-tiempo');
        const duracionSpan = tiempoElement.querySelector('.duracion');
        duracionSpan.textContent = `${minutos} min transcurridos`;
        
        console.log(`Consulta marcada como en curso: ${minutos} minutos`);
    }
}

function marcarConsultaProxima(consulta, minutosRestantes) {
    if (minutosRestantes <= 15) {
        const statusIndicator = consulta.querySelector('.status-indicator');
        if (statusIndicator && statusIndicator.classList.contains('programada')) {
            statusIndicator.style.background = 'var(--medium-criticality)';
            statusIndicator.querySelector('span').textContent = `EN ${minutosRestantes} MIN`;
            
            // Mostrar notificación si es exactamente 15, 10 o 5 minutos
            if ([15, 10, 5].includes(minutosRestantes)) {
                mostrarNotificacionConsultaProxima(consulta, minutosRestantes);
            }
        }
    }
}

function mostrarNotificacionConsultaProxima(consulta, minutos) {
    const nombrePaciente = consulta.querySelector('h3').textContent;
    
    const notification = document.createElement('div');
    notification.className = 'consulta-notification';
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
        animation: slideIn 0.5s ease;
        min-width: 300px;
    `;
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-clock" style="font-size: 20px;"></i>
            <div>
                <strong>Consulta en ${minutos} minutos</strong><br>
                <small>${nombrePaciente}</small>
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

function abrirZoom(consultaId) {
    console.log(`Abriendo Zoom para consulta: ${consultaId}`);
    
    const consulta = document.querySelector(`[data-id="${consultaId}"]`);
    const nombrePaciente = consulta.querySelector('h3').textContent;
    
    // Generar enlace de Zoom único por consulta
    const zoomLinks = {
        '001': 'https://zoom.us/j/1234567890?pwd=abcd1234',
        '002': 'https://zoom.us/j/2345678901?pwd=efgh5678',
        '003': 'https://zoom.us/j/3456789012?pwd=ijkl9012',
        '004': 'https://zoom.us/j/4567890123?pwd=mnop3456'
    };
    
    const zoomUrl = zoomLinks[consultaId] || 'https://zoom.us/j/1234567890';
    
    if (confirm(`¿Iniciar consulta virtual con ${nombrePaciente}?\n\nSe abrirá Zoom en una nueva ventana.`)) {
        // Marcar consulta como iniciada
        const statusIndicator = consulta.querySelector('.status-indicator');
        statusIndicator.className = 'status-indicator en-curso';
        statusIndicator.innerHTML = '<i class="fas fa-video"></i><span>EN ZOOM</span>';
        
        // Abrir Zoom en nueva ventana
        window.open(zoomUrl, '_blank', 'width=1200,height=800');
        
        // Registrar inicio de consulta
        registrarInicioConsulta(consultaId, nombrePaciente);
        
        // Mostrar panel de control de consulta
        mostrarPanelControlConsulta(consultaId, nombrePaciente);
        
        console.log(`Zoom abierto para ${nombrePaciente}: ${zoomUrl}`);
    }
}

function registrarInicioConsulta(consultaId, nombrePaciente) {
    const tiempoInicio = new Date().toLocaleTimeString('es-PE');
    console.log(`Consulta iniciada: ${nombrePaciente} a las ${tiempoInicio}`);
    
    // En una aplicación real, esto se registraría en la base de datos
    localStorage.setItem(`consulta_${consultaId}_inicio`, tiempoInicio);
}

function mostrarPanelControlConsulta(consultaId, nombrePaciente) {
    // Crear panel flotante de control
    const panelControl = document.createElement('div');
    panelControl.id = `panel-control-${consultaId}`;
    panelControl.className = 'panel-control-consulta';
    panelControl.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: var(--primary-blue);
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        z-index: 1000;
        min-width: 280px;
    `;
    
    panelControl.innerHTML = `
        <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 10px;">
            <strong>${nombrePaciente}</strong>
            <span id="timer-${consultaId}" style="font-family: monospace;">00:00</span>
        </div>
        <div style="display: flex; gap: 10px;">
            <button onclick="finalizarConsulta('${consultaId}')" 
                    style="background: var(--high-criticality); color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">
                <i class="fas fa-stop"></i> Finalizar
            </button>
            <button onclick="agregarNotaRapida('${consultaId}')" 
                    style="background: var(--medium-criticality); color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">
                <i class="fas fa-sticky-note"></i> Nota
            </button>
            <button onclick="cerrarPanel('${consultaId}')" 
                    style="background: var(--text-gray); color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">
                ×
            </button>
        </div>
    `;
    
    document.body.appendChild(panelControl);
    
    // Iniciar cronómetro
    iniciarCronometroConsulta(consultaId);
}

function iniciarCronometroConsulta(consultaId) {
    const inicioConsulta = new Date();
    
    const intervalo = setInterval(() => {
        const timerElement = document.getElementById(`timer-${consultaId}`);
        if (!timerElement) {
            clearInterval(intervalo);
            return;
        }
        
        const ahora = new Date();
        const diferencia = Math.floor((ahora - inicioConsulta) / 1000);
        const minutos = Math.floor(diferencia / 60);
        const segundos = diferencia % 60;
        
        timerElement.textContent = `${minutos.toString().padStart(2, '0')}:${segundos.toString().padStart(2, '0')}`;
    }, 1000);
    
    // Guardar intervalo para poder detenerlo
    window[`intervalo_${consultaId}`] = intervalo;
}

function finalizarConsulta(consultaId) {
    if (confirm('¿Finalizar la consulta?\n\nEsto cerrará la sesión de Zoom y registrará el final de la consulta.')) {
        // Detener cronómetro
        const intervalo = window[`intervalo_${consultaId}`];
        if (intervalo) {
            clearInterval(intervalo);
        }
        
        // Cerrar panel de control
        cerrarPanel(consultaId);
        
        // Marcar consulta como completada
        const consulta = document.querySelector(`[data-id="${consultaId}"]`);
        const statusIndicator = consulta.querySelector('.status-indicator');
        statusIndicator.className = 'status-indicator completada';
        statusIndicator.innerHTML = '<i class="fas fa-check-circle"></i><span>COMPLETADA</span>';
        
        // Cambiar acciones disponibles
        actualizarAccionesCompletada(consultaId);
        
        // Mostrar modal de resumen de consulta
        mostrarModalResumenConsulta(consultaId);
        
        console.log(`Consulta ${consultaId} finalizada`);
    }
}

function actualizarAccionesCompletada(consultaId) {
    const consulta = document.querySelector(`[data-id="${consultaId}"]`);
    const acciones = consulta.querySelector('.consulta-acciones');
    
    acciones.innerHTML = `
        <button class="btn-resumen" onclick="verResumenConsulta('${consultaId}')">
            <i class="fas fa-file-alt"></i> Ver Resumen
        </button>
        <button class="btn-seguimiento" onclick="programarSeguimiento('${consultaId}')">
            <i class="fas fa-calendar-plus"></i> Seguimiento
        </button>
        <button class="btn-historial" onclick="verHistorialPaciente('${consultaId}')">
            <i class="fas fa-file-medical"></i> Historial
        </button>
    `;
}

function mostrarModalResumenConsulta(consultaId) {
    const consulta = document.querySelector(`[data-id="${consultaId}"]`);
    const nombrePaciente = consulta.querySelector('h3').textContent;
    
    const resumen = prompt(`Resumen de la consulta con ${nombrePaciente}:\n\nIngrese las conclusiones principales:`);
    
    if (resumen && resumen.trim()) {
        // Agregar resumen a la consulta
        const descripcion = consulta.querySelector('.consulta-descripcion');
        const resumenElement = document.createElement('div');
        resumenElement.style.cssText = `
            background: #e8f5e8;
            border-left: 3px solid var(--positive-change);
            padding: 10px;
            margin-top: 10px;
            border-radius: 4px;
        `;
        resumenElement.innerHTML = `
            <strong>Resumen de Consulta:</strong><br>
            ${resumen}<br>
            <small style="color: var(--text-gray);">Completada: ${new Date().toLocaleString('es-PE')}</small>
        `;
        
        descripcion.appendChild(resumenElement);
        
        console.log(`Resumen agregado para consulta ${consultaId}`);
    }
}

function cerrarPanel(consultaId) {
    const panel = document.getElementById(`panel-control-${consultaId}`);
    if (panel) {
        panel.remove();
    }
}

function agregarNotaRapida(consultaId) {
    const nota = prompt('Nota rápida durante la consulta:');
    
    if (nota && nota.trim()) {
        const consulta = document.querySelector(`[data-id="${consultaId}"]`);
        const descripcion = consulta.querySelector('.consulta-descripcion');
        
        const notaElement = document.createElement('div');
        notaElement.style.cssText = `
            background: #fff3cd;
            border-left: 3px solid var(--medium-criticality);
            padding: 8px;
            margin-top: 8px;
            border-radius: 4px;
            font-size: 0.9em;
        `;
        notaElement.innerHTML = `
            <strong>Nota:</strong> ${nota}<br>
            <small style="color: var(--text-gray);">${new Date().toLocaleTimeString('es-PE')}</small>
        `;
        
        descripcion.appendChild(notaElement);
        
        console.log(`Nota rápida agregada: ${nota}`);
    }
}

function testearZoom(consultaId) {
    console.log(`Iniciando test de Zoom para consulta: ${consultaId}`);
    
    // Mostrar modal de test
    document.getElementById('modal-test-zoom').style.display = 'flex';
    
    // Simular proceso de test
    setTimeout(() => {
        const testItems = document.querySelectorAll('.test-item');
        
        // Test de audio y video
        setTimeout(() => {
            const audioTest = testItems[2].querySelector('.test-status');
            audioTest.innerHTML = '<i class="fas fa-check-circle" style="color: var(--positive-change);"></i>';
            testItems[2].querySelector('.test-descripcion').innerHTML = `
                <strong>Audio y Video</strong><br>
                Micrófono y cámara funcionando correctamente
            `;
        }, 2000);
        
        // Test de conexión con paciente
        setTimeout(() => {
            const conexionTest = testItems[3].querySelector('.test-status');
            conexionTest.innerHTML = '<i class="fas fa-check-circle" style="color: var(--positive-change);"></i>';
            testItems[3].querySelector('.test-descripcion').innerHTML = `
                <strong>Conexión con Paciente</strong><br>
                Listo para iniciar consulta
            `;
        }, 4000);
        
    }, 1000);
}

function completarTest() {
    cerrarModalTest();
    
    // Simular que el test fue exitoso y abrir Zoom
    const consultaId = '003'; // ID de la consulta que se está testeando
    setTimeout(() => {
        abrirZoom(consultaId);
    }, 500);
}

function testearZoomGeneral() {
    console.log('Ejecutando test general de Zoom');
    
    const boton = document.querySelector('.btn-test-general');
    const textoOriginal = boton.innerHTML;
    
    boton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Testeando...';
    boton.disabled = true;
    
    setTimeout(() => {
        boton.innerHTML = '<i class="fas fa-check"></i> Test Exitoso';
        boton.style.background = 'var(--positive-change)';
        
        setTimeout(() => {
            boton.innerHTML = textoOriginal;
            boton.style.background = '';
            boton.disabled = false;
        }, 3000);
    }, 3000);
}

function prepararConsulta(consultaId) {
    const consulta = document.querySelector(`[data-id="${consultaId}"]`);
    const nombrePaciente = consulta.querySelector('h3').textContent;
    
    if (confirm(`¿Preparar consulta presencial con ${nombrePaciente}?`)) {
        // Marcar como en preparación
        const statusIndicator = consulta.querySelector('.status-indicator');
        statusIndicator.style.background = 'var(--medium-criticality)';
        statusIndicator.querySelector('span').textContent = 'PREPARANDO';
        
        // Mostrar checklist de preparación
        mostrarChecklistPreparacion(consultaId, nombrePaciente);
        
        console.log(`Preparando consulta presencial: ${nombrePaciente}`);
    }
}

function mostrarChecklistPreparacion(consultaId, nombrePaciente) {
    const checklist = [
        'Revisar historial médico',
        'Preparar equipos médicos',
        'Verificar resultados de exámenes',
        'Revisar medicación actual',
        'Preparar consultorio'
    ];
    
    const checklistHtml = checklist.map((item, index) => 
        `<label style="display: flex; align-items: center; gap: 8px; margin: 5px 0;">
            <input type="checkbox" onchange="verificarChecklist('${consultaId}')"> ${item}
        </label>`
    ).join('');
    
    if (confirm(`Checklist de preparación para ${nombrePaciente}:\n\n${checklist.join('\n')}\n\n¿Continuar con la preparación?`)) {
        console.log('Checklist iniciado');
    }
}

function verHistorialPaciente(consultaId) {
    console.log(`Ver historial del paciente de consulta: ${consultaId}`);
    
    const consulta = document.querySelector(`[data-id="${consultaId}"]`);
    const nombrePaciente = consulta.querySelector('h3').textContent;
    
    // En una aplicación real, esto abriría el historial médico completo
    alert(`Abriendo historial médico completo de:\n${nombrePaciente}\n\nSe cargará en una nueva ventana con:\n• Diagnósticos previos\n• Tratamientos actuales\n• Resultados de exámenes\n• Evolución biométrica`);
}

function reprogramarConsulta(consultaId) {
    const consulta = document.querySelector(`[data-id="${consultaId}"]`);
    const nombrePaciente = consulta.querySelector('h3').textContent;
    
    if (confirm(`¿Reprogramar consulta de ${nombrePaciente}?`)) {
        console.log(`Reprogramando consulta: ${consultaId}`);
        
        // En una aplicación real, esto redirigiría al calendario
        alert(`Redirigiendo al calendario para reprogramar consulta de ${nombrePaciente}...`);
    }
}

function agregarNotas(consultaId) {
    const nota = prompt('Agregar nota a la consulta:');
    
    if (nota && nota.trim()) {
        const consulta = document.querySelector(`[data-id="${consultaId}"]`);
        const descripcion = consulta.querySelector('.consulta-descripcion');
        
        const notaElement = document.createElement('div');
        notaElement.style.cssText = `
            background: #f8f9fa;
            border-left: 3px solid var(--secondary-blue);
            padding: 8px;
            margin-top: 8px;
            border-radius: 4px;
            font-size: 0.9em;
        `;
        notaElement.innerHTML = `
            <strong>Nota:</strong> ${nota}<br>
            <small style="color: var(--text-gray);">${new Date().toLocaleString('es-PE')}</small>
        `;
        
        descripcion.appendChild(notaElement);
        
        console.log(`Nota agregada a consulta ${consultaId}: ${nota}`);
    }
}

function verResumenConsulta(consultaId) {
    const consulta = document.querySelector(`[data-id="${consultaId}"]`);
    const nombrePaciente = consulta.querySelector('h3').textContent;
    
    console.log(`Ver resumen de consulta completada: ${consultaId}`);
    
    alert(`Resumen de Consulta Completada\n\nPaciente: ${nombrePaciente}\nDuración: 28 minutos\nTipo: Virtual\n\nConclusiones:\n• Paciente estable\n• Continuar tratamiento actual\n• Próximo control en 1 mes`);
}

function programarSeguimiento(consultaId) {
    const consulta = document.querySelector(`[data-id="${consultaId}"]`);
    const nombrePaciente = consulta.querySelector('h3').textContent;
    
    if (confirm(`¿Programar consulta de seguimiento para ${nombrePaciente}?`)) {
        console.log(`Programando seguimiento para: ${nombrePaciente}`);
        
        alert(`Redirigiendo al calendario para programar seguimiento de ${nombrePaciente}...\n\nSugerencia automática:\n• Fecha: En 1 mes\n• Tipo: Virtual\n• Duración: 30 minutos`);
    }
}

function aplicarFiltros() {
    const fecha = document.getElementById('filtro-fecha').value;
    const tipo = document.getElementById('filtro-tipo').value;
    const estado = document.getElementById('filtro-estado').value;
    
    console.log('Aplicando filtros:', { fecha, tipo, estado });
    
    const consultas = document.querySelectorAll('.consulta-card');
    let consultasVisibles = 0;
    
    consultas.forEach(consulta => {
        let mostrar = true;
        
        // Filtro por tipo
        if (tipo !== 'todas') {
            const tipoConsulta = consulta.getAttribute('data-tipo');
            if (tipoConsulta !== tipo) {
                mostrar = false;
            }
        }
        
        // Filtro por estado
        if (estado !== 'todas') {
            const estadoConsulta = consulta.getAttribute('data-estado');
            if (estadoConsulta !== estado) {
                mostrar = false;
            }
        }
        
        consulta.style.display = mostrar ? 'block' : 'none';
        if (mostrar) consultasVisibles++;
    });
    
    // Mostrar resultado de filtros
    console.log(`Filtros aplicados: ${consultasVisibles} consultas visibles`);
}

function actualizarConsultas() {
    console.log('Actualizando lista de consultas...');
    
    const boton = document.querySelector('.btn-actualizar');
    const textoOriginal = boton.innerHTML;
    
    boton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Actualizando...';
    boton.disabled = true;
    
    setTimeout(() => {
        boton.innerHTML = textoOriginal;
        boton.disabled = false;
        
        // Simular actualización
        actualizarTiemposReales();
        verificarConsultasProximas();
        
        console.log('Consultas actualizadas');
    }, 2000);
}

function verCalendario() {
    console.log('Redirigiendo al calendario médico...');
    
    // En una aplicación real, esto redirigiría a la página del calendario
    window.location.href = '/medico/mi_calendario';
}

function toggleConsultasSemana() {
    const contenido = document.getElementById('consultas-semana-contenido');
    const boton = document.querySelector('.btn-toggle-semana i');
    
    if (contenido.style.display === 'none') {
        contenido.style.display = 'block';
        boton.className = 'fas fa-chevron-up';
    } else {
        contenido.style.display = 'none';
        boton.className = 'fas fa-chevron-down';
    }
}

function verificarConsultasProximas() {
    console.log('Verificando consultas próximas...');
    
    // Esta función se ejecutaría periódicamente para verificar
    // consultas que están por comenzar y enviar notificaciones
    
    actualizarTiemposReales();
}

function cerrarModalTest() {
    document.getElementById('modal-test-zoom').style.display = 'none';
    
    // Resetear el estado del test
    const testItems = document.querySelectorAll('.test-item');
    if (testItems.length > 2) {
        // Reset audio y video
        testItems[2].querySelector('.test-status').innerHTML = '<i class="fas fa-clock" style="color: var(--text-gray);"></i>';
        testItems[2].querySelector('.test-descripcion').innerHTML = `
            <strong>Audio y Video</strong><br>
            Verificando dispositivos...
        `;
        
        // Reset conexión
        testItems[3].querySelector('.test-status').innerHTML = '<i class="fas fa-clock" style="color: var(--text-gray);"></i>';
        testItems[3].querySelector('.test-descripcion').innerHTML = `
            <strong>Conexión con Paciente</strong><br>
            Esperando verificación...
        `;
    }
}

// Cerrar modal con ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        cerrarModalTest();
    }
});

// Agregar animación CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
`;
document.head.appendChild(style);