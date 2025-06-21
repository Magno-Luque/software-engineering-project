// static/js/desktop/medico-pacientes.js
document.addEventListener('DOMContentLoaded', () => {
    console.log('Módulo de pacientes cargado.');
    
    // Inicializar funcionalidades
    initFiltros();
    initBusqueda();
});

function aplicarFiltros() {
    const estado = document.getElementById('filtro-estado').value;
    const enfermedad = document.getElementById('filtro-enfermedad').value;
    const riesgo = document.getElementById('filtro-riesgo').value;
    const busqueda = document.getElementById('busqueda-paciente').value.toLowerCase();
    
    console.log('Aplicando filtros:', { estado, enfermedad, riesgo, busqueda });
    
    const filas = document.querySelectorAll('#tabla-pacientes tr');
    
    filas.forEach(fila => {
        let mostrar = true;
        
        // Filtro por texto de búsqueda
        if (busqueda) {
            const textoFila = fila.textContent.toLowerCase();
            if (!textoFila.includes(busqueda)) {
                mostrar = false;
            }
        }
        
        // Filtro por estado (se podría implementar con data attributes)
        if (estado !== 'todos') {
            // Lógica para filtrar por estado
        }
        
        // Filtro por enfermedad
        if (enfermedad !== 'todas') {
            const enfermedadCelda = fila.querySelector('td:nth-child(4)');
            if (enfermedadCelda) {
                const textoEnfermedad = enfermedadCelda.textContent.toLowerCase();
                if (!textoEnfermedad.includes(enfermedad)) {
                    mostrar = false;
                }
            }
        }
        
        // Filtro por riesgo
        if (riesgo !== 'todos') {
            const riesgoCelda = fila.querySelector('td:nth-child(5)');
            if (riesgoCelda) {
                const textoRiesgo = riesgoCelda.textContent.toLowerCase();
                if (!textoRiesgo.includes(riesgo)) {
                    mostrar = false;
                }
            }
        }
        
        fila.style.display = mostrar ? '' : 'none';
    });
    
    // Mostrar mensaje si no hay resultados
    const filasVisibles = Array.from(filas).filter(fila => fila.style.display !== 'none');
    if (filasVisibles.length === 0) {
        mostrarMensajeSinResultados();
    } else {
        ocultarMensajeSinResultados();
    }
}

function initFiltros() {
    // Event listeners para filtros en tiempo real
    document.getElementById('busqueda-paciente').addEventListener('input', aplicarFiltros);
    document.getElementById('filtro-estado').addEventListener('change', aplicarFiltros);
    document.getElementById('filtro-enfermedad').addEventListener('change', aplicarFiltros);
    document.getElementById('filtro-riesgo').addEventListener('change', aplicarFiltros);
}

function initBusqueda() {
    // Búsqueda con Enter
    document.getElementById('busqueda-paciente').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            aplicarFiltros();
        }
    });
}

function verPaciente(pacienteId) {
    console.log(`Ver detalles del paciente: ${pacienteId}`);
    
    // En una aplicación real, esto abriría un modal o nueva página
    alert(`Mostrando detalles del paciente ${pacienteId}\n\nEsta funcionalidad abrirá:\n- Información personal\n- Estado actual\n- Próximas citas\n- Notas del médico`);
}

function verHistorial(pacienteId) {
    console.log(`Ver historial del paciente: ${pacienteId}`);
    
    // Obtener datos del paciente (simulado)
    const pacienteDatos = obtenerDatosPaciente(pacienteId);
    
    // Actualizar título del modal
    document.getElementById('historial-titulo').textContent = `Historial Clínico - ${pacienteDatos.nombre}`;
    
    // Mostrar modal
    document.getElementById('modal-historial').style.display = 'flex';
    
    // Cargar datos del historial
    cargarHistorialPaciente(pacienteId);
}

function obtenerDatosPaciente(pacienteId) {
    // Simulación de datos del paciente
    const pacientes = {
        '001': { nombre: 'Juan Pérez García', dni: '12345678' },
        '002': { nombre: 'María Elena González', dni: '87654321' },
        '003': { nombre: 'Carlos Alberto Rodríguez', dni: '11223344' }
    };
    
    return pacientes[pacienteId] || { nombre: 'Paciente Desconocido', dni: 'N/A' };
}

function cargarHistorialPaciente(pacienteId) {
    console.log(`Cargando historial para paciente: ${pacienteId}`);
    
    // En una aplicación real, esto haría una llamada API
    // fetch(`/api/medico/paciente/${pacienteId}/historial`)
    
    // Simular carga de gráfico de glucosa
    setTimeout(() => {
        dibujarGraficoGlucosa();
    }, 100);
}

function mostrarTab(tabName) {
    // Ocultar todos los tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Desactivar todos los botones
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Mostrar tab seleccionado
    document.getElementById(`tab-${tabName}`).classList.add('active');
    
    // Activar botón correspondiente
    event.target.classList.add('active');
    
    // Si es el tab de biométricos, redibujar gráfico
    if (tabName === 'biometricos') {
        setTimeout(() => {
            dibujarGraficoGlucosa();
        }, 100);
    }
}

function dibujarGraficoGlucosa() {
    const canvas = document.getElementById('grafico-glucosa');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Limpiar canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Datos simulados de glucosa (últimos 30 días)
    const datos = [
        180, 165, 145, 170, 160, 155, 140, 135, 150, 165,
        175, 160, 145, 150, 155, 160, 170, 165, 155, 150,
        145, 160, 175, 180, 170, 165, 160, 155, 150, 240
    ];
    
    const maxValor = Math.max(...datos);
    const minValor = Math.min(...datos);
    const rango = maxValor - minValor;
    
    // Configuración del gráfico
    const padding = 40;
    const chartWidth = canvas.width - (padding * 2);
    const chartHeight = canvas.height - (padding * 2);
    
    // Dibujar ejes
    ctx.strokeStyle = '#ccc';
    ctx.lineWidth = 1;
    
    // Eje Y
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, canvas.height - padding);
    ctx.stroke();
    
    // Eje X
    ctx.beginPath();
    ctx.moveTo(padding, canvas.height - padding);
    ctx.lineTo(canvas.width - padding, canvas.height - padding);
    ctx.stroke();
    
    // Dibujar líneas de referencia
    ctx.strokeStyle = '#f0f0f0';
    ctx.lineWidth = 0.5;
    
    // Línea de objetivo (120 mg/dL)
    const objetivoY = canvas.height - padding - ((120 - minValor) / rango) * chartHeight;
    ctx.beginPath();
    ctx.moveTo(padding, objetivoY);
    ctx.lineTo(canvas.width - padding, objetivoY);
    ctx.stroke();
    
    // Dibujar la línea de datos
    ctx.strokeStyle = '#2563EB';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    datos.forEach((valor, index) => {
        const x = padding + (index / (datos.length - 1)) * chartWidth;
        const y = canvas.height - padding - ((valor - minValor) / rango) * chartHeight;
        
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    
    ctx.stroke();
    
    // Dibujar puntos
    ctx.fillStyle = '#2563EB';
    datos.forEach((valor, index) => {
        const x = padding + (index / (datos.length - 1)) * chartWidth;
        const y = canvas.height - padding - ((valor - minValor) / rango) * chartHeight;
        
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, 2 * Math.PI);
        ctx.fill();
    });
    
    // Etiquetas
    ctx.fillStyle = '#666';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    
    // Etiqueta del objetivo
    ctx.fillText('Objetivo: 120 mg/dL', canvas.width / 2, objetivoY - 10);
    
    // Valor más reciente (último punto)
    const ultimoIndex = datos.length - 1;
    const ultimoX = padding + (ultimoIndex / (datos.length - 1)) * chartWidth;
    const ultimoY = canvas.height - padding - ((datos[ultimoIndex] - minValor) / rango) * chartHeight;
    
    ctx.fillStyle = '#dc3545';
    ctx.fillText(`${datos[ultimoIndex]} mg/dL`, ultimoX, ultimoY - 10);
}

function editarPaciente(pacienteId) {
    console.log(`Editar paciente: ${pacienteId}`);
    
    const pacienteDatos = obtenerDatosPaciente(pacienteId);
    
    if (confirm(`¿Desea editar la información de ${pacienteDatos.nombre}?`)) {
        // En una aplicación real, esto abriría un formulario de edición
        alert(`Abriendo formulario de edición para:\n\n` +
              `Paciente: ${pacienteDatos.nombre}\n` +
              `DNI: ${pacienteDatos.dni}\n\n` +
              `Podrá modificar:\n` +
              `- Datos personales\n` +
              `- Plan de tratamiento\n` +
              `- Medicamentos\n` +
              `- Notas médicas`);
    }
}

function cerrarHistorial() {
    document.getElementById('modal-historial').style.display = 'none';
}

function agregarNota() {
    const nota = prompt('Ingrese una nueva nota médica:');
    
    if (nota && nota.trim()) {
        // En una aplicación real, esto enviaría la nota al servidor
        console.log('Nueva nota médica:', nota);
        
        // Simular agregar la nota al historial
        const fechaActual = new Date().toLocaleDateString('es-PE');
        const nuevaNota = `
            <div class="historial-item" style="background: #f0fff4; border-left: 3px solid #28a745;">
                <div class="historial-fecha">${fechaActual}</div>
                <div class="historial-detalle">
                    <strong>Nota Médica</strong><br>
                    ${nota}
                    <br><small>Dr. José Pérez - Cardiología</small>
                </div>
            </div>
        `;
        
        // Agregar al tab de diagnósticos
        const diagnosticosTab = document.querySelector('#tab-diagnosticos .historial-section');
        diagnosticosTab.insertAdjacentHTML('afterbegin', nuevaNota);
        
        alert('Nota médica agregada correctamente.');
    }
}

function mostrarMensajeSinResultados() {
    // Verificar si ya existe el mensaje
    if (document.getElementById('sin-resultados')) return;
    
    const tabla = document.getElementById('tabla-pacientes');
    const mensaje = document.createElement('tr');
    mensaje.id = 'sin-resultados';
    mensaje.innerHTML = `
        <td colspan="8" style="text-align: center; padding: 40px; color: var(--text-gray);">
            <i class="fas fa-search" style="font-size: 48px; margin-bottom: 15px; opacity: 0.3;"></i><br>
            <strong>No se encontraron pacientes</strong><br>
            <small>Intente modificar los filtros de búsqueda</small>
        </td>
    `;
    
    tabla.appendChild(mensaje);
}

function ocultarMensajeSinResultados() {
    const mensaje = document.getElementById('sin-resultados');
    if (mensaje) {
        mensaje.remove();
    }
}

// Cerrar modal al hacer clic fuera de él
document.addEventListener('click', (e) => {
    const modal = document.getElementById('modal-historial');
    if (e.target === modal) {
        cerrarHistorial();
    }
});

// Cerrar modal con ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const modal = document.getElementById('modal-historial');
        if (modal.style.display === 'flex') {
            cerrarHistorial();
        }
    }
});

// Función para exportar datos del paciente (funcionalidad adicional)
function exportarPaciente(pacienteId) {
    console.log(`Exportando datos del paciente: ${pacienteId}`);
    
    const pacienteDatos = obtenerDatosPaciente(pacienteId);
    
    // Simular exportación
    alert(`Exportando historial completo de ${pacienteDatos.nombre}\n\n` +
          `El archivo incluirá:\n` +
          `- Datos personales\n` +
          `- Historial médico completo\n` +
          `- Gráficos de evolución\n` +
          `- Tratamientos y medicamentos\n\n` +
          `Formato: PDF | Descarga iniciada...`);
}

// Función para programar cita rápida
function programarCita(pacienteId) {
    const pacienteDatos = obtenerDatosPaciente(pacienteId);
    
    if (confirm(`¿Desea programar una cita con ${pacienteDatos.nombre}?`)) {
        // En una aplicación real, esto redirigiría al calendario
        window.location.href = `/medico/mi_calendario?paciente=${pacienteId}`;
    }
}