// static/js/desktop/medico-dashboard.js
document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard médico cargado.');

    // Funcionalidad para las alertas críticas
    initAlertasCriticas();
    
    // Actualizar datos cada 30 segundos
    setInterval(actualizarDashboard, 30000);
    
    // Inicializar notificaciones de nuevas alertas
    initNotificacionesAlertas();
});

function initAlertasCriticas() {
    // Botones de contactar en alertas
    const botonesContactar = document.querySelectorAll('.btn-contactar');
    botonesContactar.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const alertaElement = e.target.closest('.alerta-critica, .alerta-media, .alerta-baja');
            const paciente = alertaElement.querySelector('.alerta-paciente').textContent;
            contactarPaciente(paciente);
        });
    });

    // Botones de resolver en alertas
    const botonesResolver = document.querySelectorAll('.btn-resolver');
    botonesResolver.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const alertaElement = e.target.closest('.alerta-critica, .alerta-media, .alerta-baja');
            const paciente = alertaElement.querySelector('.alerta-paciente').textContent;
            resolverAlerta(alertaElement, paciente);
        });
    });
}

function contactarPaciente(nombrePaciente) {
    // Mostrar modal o realizar acción de contacto
    if (confirm(`¿Desea contactar a ${nombrePaciente}?`)) {
        console.log(`Contactando a ${nombrePaciente}...`);
        
        // Aquí se podría integrar con sistema de llamadas o mensajería
        alert(`Iniciando contacto con ${nombrePaciente}.\nSe abrirá el sistema de comunicación.`);
        
        // En un sistema real, esto podría:
        // - Abrir el dialer del sistema
        // - Iniciar una videollamada
        // - Enviar notificación al cuidador
        // - Registrar el intento de contacto
    }
}

function resolverAlerta(alertaElement, nombrePaciente) {
    if (confirm(`¿Marcar como resuelto la alerta de ${nombrePaciente}?`)) {
        // Animación de resolución
        alertaElement.style.transition = 'opacity 0.5s ease';
        alertaElement.style.opacity = '0.5';
        
        // Simular llamada API
        setTimeout(() => {
            alertaElement.style.background = '#f0fff4';
            alertaElement.style.borderLeftColor = 'var(--positive-change)';
            
            // Cambiar contenido
            const acciones = alertaElement.querySelector('.alerta-acciones');
            acciones.innerHTML = '<span style="color: var(--positive-change); font-weight: bold;"><i class="fas fa-check-circle"></i> Resuelto</span>';
            
            // Actualizar contador de alertas
            actualizarContadorAlertas();
            
        }, 500);
        
        console.log(`Alerta de ${nombrePaciente} marcada como resuelta.`);
    }
}

function actualizarContadorAlertas() {
    // Actualizar el número en la tarjeta de estadísticas
    const statNumber = document.querySelector('.stat-card:nth-child(3) .stat-number');
    const currentCount = parseInt(statNumber.textContent);
    if (currentCount > 0) {
        statNumber.textContent = currentCount - 1;
    }
    
    // Actualizar badge de notificaciones si existe
    const badge = document.querySelector('.notifications .badge');
    if (badge) {
        const badgeCount = parseInt(badge.textContent);
        if (badgeCount > 0) {
            badge.textContent = badgeCount - 1;
        }
    }
}

function actualizarDashboard() {
    // Función para actualizar datos del dashboard periódicamente
    console.log('Actualizando datos del dashboard...');
    
    // En una aplicación real, esto haría:
    // - Fetch a /api/medico/dashboard-data
    // - Actualizar contadores
    // - Verificar nuevas alertas
    // - Actualizar lista de citas
    
    // Simulación de actualización
    const timestamp = new Date().toLocaleTimeString();
    console.log(`Dashboard actualizado a las ${timestamp}`);
}

function initNotificacionesAlertas() {
    // Simular llegada de nuevas alertas críticas
    // En producción esto vendría de WebSocket o Server-Sent Events
    
    setInterval(() => {
        // Simulación aleatoria de nueva alerta (5% probabilidad cada 30 segundos)
        if (Math.random() < 0.05) {
            mostrarNuevaAlerta();
        }
    }, 30000);
}

function mostrarNuevaAlerta() {
    // Crear notificación de nueva alerta
    const notification = document.createElement('div');
    notification.className = 'nueva-alerta-notification';
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--high-criticality);
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 1000;
        animation: slideIn 0.5s ease;
    `;
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-exclamation-triangle"></i>
            <div>
                <strong>Nueva Alerta Crítica</strong><br>
                <small>Un paciente requiere atención inmediata</small>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: white; font-size: 18px; cursor: pointer;">×</button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Reproducir sonido de alerta (opcional)
    reproducirSonidoAlerta();
    
    // Auto-remover después de 10 segundos
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 10000);
    
    // Actualizar contador
    const statNumber = document.querySelector('.stat-card:nth-child(3) .stat-number');
    const currentCount = parseInt(statNumber.textContent);
    statNumber.textContent = currentCount + 1;
    
    // Actualizar badge
    const badge = document.querySelector('.notifications .badge');
    if (badge) {
        const badgeCount = parseInt(badge.textContent);
        badge.textContent = badgeCount + 1;
    }
}

function reproducirSonidoAlerta() {
    // Reproducir sonido de alerta si está habilitado
    // En una aplicación real, esto sería configurable por el médico
    try {
        const audio = new Audio('/static/sounds/alert-beep.mp3');
        audio.volume = 0.3;
        audio.play().catch(e => {
            console.log('No se pudo reproducir el sonido de alerta:', e);
        });
    } catch (e) {
        console.log('Audio no disponible');
    }
}

// Añadir estilos CSS para animación
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);