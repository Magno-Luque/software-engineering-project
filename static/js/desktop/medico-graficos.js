// static/js/desktop/medico-graficos.js
document.addEventListener('DOMContentLoaded', () => {
    console.log('Página de gráficos médicos cargada.');

    // Inicializar funcionalidades
    initSelectoresPaciente();
    initCambioTipoGrafico();
    initAgregarNota();
});

// Datos simulados de pacientes
const datosPacientes = {
    'juan-perez': {
        nombre: 'Juan Pérez García',
        enfermedad: 'Diabetes Tipo 2',
        edad: '45 años',
        estado: 'ACTIVO',
        adherencia: 85,
        medicacion: 92,
        registros: 28,
        tendencia: 'Mejorando',
        glucosa: [220, 200, 180, 165, 150, 140, 135, 130, 125, 120, 115, 110, 105],
        presion: [140, 138, 135, 132, 130, 128, 125, 122, 120, 118, 115, 112, 110],
        peso: [85, 84.8, 84.5, 84.2, 84.0, 83.8, 83.5, 83.2, 83.0, 82.8, 82.5, 82.2, 82.0]
    },
    'maria-gonzalez': {
        nombre: 'María González Ruiz',
        enfermedad: 'Hipertensión Arterial',
        edad: '52 años',
        estado: 'ACTIVO',
        adherencia: 78,
        medicacion: 85,
        registros: 25,
        tendencia: 'Estable',
        glucosa: [95, 98, 92, 96, 94, 97, 93, 95, 91, 94, 96, 93, 95],
        presion: [165, 160, 155, 150, 148, 145, 142, 140, 138, 135, 132, 130, 128],
        peso: [72, 71.8, 71.6, 71.4, 71.2, 71.0, 70.8, 70.6, 70.4, 70.2, 70.0, 69.8, 69.6]
    },
    'carlos-silva': {
        nombre: 'Carlos Silva Rodríguez',
        enfermedad: 'EPOC',
        edad: '38 años',
        estado: 'ACTIVO',
        adherencia: 90,
        medicacion: 95,
        registros: 30,
        tendencia: 'Excelente',
        glucosa: [88, 90, 85, 87, 89, 86, 88, 84, 86, 88, 85, 87, 84],
        presion: [125, 123, 120, 118, 115, 112, 110, 108, 105, 102, 100, 98, 95],
        peso: [78, 78.2, 78.4, 78.6, 78.8, 79.0, 79.2, 79.4, 79.6, 79.8, 80.0, 80.2, 80.4]
    }
};

function initSelectoresPaciente() {
    const selectorPaciente = document.getElementById('selectorPaciente');
    const selectorPeriodo = document.getElementById('selectorPeriodo');
    const btnActualizar = document.getElementById('actualizarGraficos');

    // Evento de cambio de paciente
    selectorPaciente.addEventListener('change', () => {
        const pacienteId = selectorPaciente.value;
        if (pacienteId) {
            mostrarGraficosPaciente(pacienteId);
        } else {
            ocultarGraficos();
        }
    });

    // Evento de actualizar
    btnActualizar.addEventListener('click', () => {
        const pacienteId = selectorPaciente.value;
        if (pacienteId) {
            actualizarGraficos(pacienteId);
        } else {
            alert('Por favor seleccione un paciente primero.');
        }
    });
}

function mostrarGraficosPaciente(pacienteId) {
    const paciente = datosPacientes[pacienteId];
    if (!paciente) return;

    // Ocultar mensaje de selección
    document.getElementById('mensajeSeleccion').style.display = 'none';
    
    // Mostrar contenedor de gráficos
    document.getElementById('graficosContainer').style.display = 'block';

    // Actualizar información del paciente
    document.getElementById('nombrePaciente').textContent = paciente.nombre;
    document.getElementById('enfermedad').textContent = paciente.enfermedad;
    document.getElementById('edadPaciente').textContent = paciente.edad;
    document.getElementById('estadoPaciente').textContent = paciente.estado;

    // Actualizar métricas
    document.getElementById('adherenciaTotal').textContent = paciente.adherencia + '%';
    document.getElementById('medicacionTomada').textContent = paciente.medicacion + '%';
    document.getElementById('registrosDiarios').textContent = paciente.registros;
    document.getElementById('tendenciaGeneral').textContent = paciente.tendencia;

    // Actualizar colores según tendencia
    const cambioAdherencia = document.getElementById('cambioAdherencia');
    const cambioMedicacion = document.getElementById('cambioMedicacion');
    
    if (paciente.adherencia > 80) {
        cambioAdherencia.className = 'stat-change positive';
        cambioAdherencia.textContent = '+' + (paciente.adherencia - 80) + '% vs objetivo';
    } else {
        cambioAdherencia.className = 'stat-change negative';
        cambioAdherencia.textContent = '-' + (80 - paciente.adherencia) + '% del objetivo';
    }

    // Actualizar gráfico principal
    actualizarGraficoPrincipal(paciente, 'glucosa');

    console.log(`Mostrando gráficos para: ${paciente.nombre}`);
}

function ocultarGraficos() {
    document.getElementById('mensajeSeleccion').style.display = 'block';
    document.getElementById('graficosContainer').style.display = 'none';
}

function actualizarGraficos(pacienteId) {
    console.log('Actualizando gráficos...');
    
    // Simular carga
    const btnActualizar = document.getElementById('actualizarGraficos');
    const textoOriginal = btnActualizar.innerHTML;
    
    btnActualizar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Actualizando...';
    btnActualizar.disabled = true;

    setTimeout(() => {
        mostrarGraficosPaciente(pacienteId);
        btnActualizar.innerHTML = textoOriginal;
        btnActualizar.disabled = false;
        
        // Mostrar notificación de éxito
        mostrarNotificacion('Gráficos actualizados correctamente', 'success');
    }, 1500);
}

function initCambioTipoGrafico() {
    const selectorTipo = document.getElementById('tipoGrafico');
    
    selectorTipo.addEventListener('change', () => {
        const pacienteId = document.getElementById('selectorPaciente').value;
        const tipoGrafico = selectorTipo.value;
        
        if (pacienteId) {
            const paciente = datosPacientes[pacienteId];
            actualizarGraficoPrincipal(paciente, tipoGrafico);
        }
    });
}

function actualizarGraficoPrincipal(paciente, tipo) {
    const datos = paciente[tipo];
    if (!datos) return;

    // Actualizar título del gráfico
    const titulos = {
        'glucosa': 'Evolución de Glucosa en Sangre',
        'presion': 'Evolución de Presión Arterial',
        'peso': 'Evolución del Peso',
        'hemoglobina': 'Evolución de Hemoglobina A1C'
    };
    
    document.querySelector('.grafico-container h2').textContent = titulos[tipo];

    // Generar puntos para el SVG
    const width = 600;
    const height = 360;
    const maxVal = Math.max(...datos);
    const minVal = Math.min(...datos);
    const range = maxVal - minVal;
    
    let puntos = '';
    let circulos = '';
    
    datos.forEach((valor, index) => {
        const x = (index / (datos.length - 1)) * width;
        const y = height - ((valor - minVal) / range) * height;
        
        puntos += `${x},${y} `;
        
        // Determinar color del punto según el valor
        let color = 'var(--positive-change)';
        if (tipo === 'glucosa') {
            if (valor > 180) color = 'var(--high-criticality)';
            else if (valor > 140) color = 'var(--medium-criticality)';
        } else if (tipo === 'presion') {
            if (valor > 140) color = 'var(--high-criticality)';
            else if (valor > 120) color = 'var(--medium-criticality)';
        }
        
        circulos += `<circle cx="${x}" cy="${y}" r="4" fill="${color}"/>`;
    });

    // Actualizar SVG
    const svg = document.getElementById('graficoSVG');
    svg.innerHTML = `
        <polyline points="${puntos.trim()}" 
                  fill="none" 
                  stroke="var(--secondary-blue)" 
                  stroke-width="3"
                  stroke-linecap="round"/>
        ${circulos}
    `;

    // Actualizar eje Y con valores apropiados
    const ejeY = document.querySelector('.grafico-container > div > div > div');
    const unidades = {
        'glucosa': 'mg/dL',
        'presion': 'mmHg',
        'peso': 'kg',
        'hemoglobina': '%'
    };
    
    console.log(`Gráfico actualizado: ${tipo} para ${paciente.nombre}`);
}

function initAgregarNota() {
    const btnAgregar = document.getElementById('agregarNota');
    
    btnAgregar.addEventListener('click', () => {
        const pacienteId = document.getElementById('selectorPaciente').value;
        if (!pacienteId) {
            alert('Por favor seleccione un paciente primero.');
            return;
        }
        
        mostrarModalNota();
    });
}

function mostrarModalNota() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    `;
    
    modal.innerHTML = `
        <div class="modal-content" style="
            background: white;
            padding: 30px;
            border-radius: 10px;
            width: 500px;
            max-width: 90%;
        ">
            <h3 style="margin-bottom: 20px;">Agregar Nota Médica</h3>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold;">Tipo de Nota:</label>
                <select id="tipoNota" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                    <option value="observacion">📋 Observación</option>
                    <option value="recomendacion">💡 Recomendación</option>
                    <option value="alerta">⚠️ Atención</option>
                    <option value="mejora">📈 Mejora</option>
                </select>
            </div>
            
            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 5px; font-weight: bold;">Nota:</label>
                <textarea id="textoNota" style="
                    width: 100%; 
                    height: 120px; 
                    padding: 10px; 
                    border: 1px solid #ddd; 
                    border-radius: 4px;
                    resize: vertical;
                " placeholder="Escriba su nota médica aquí..."></textarea>
            </div>
            
            <div style="display: flex; gap: 10px; justify-content: flex-end;">
                <button class="btn-cancelar" style="
                    padding: 10px 20px;
                    border: 1px solid #ddd;
                    background: white;
                    border-radius: 4px;
                    cursor: pointer;
                ">Cancelar</button>
                <button class="btn-guardar" style="
                    padding: 10px 20px;
                    background: var(--secondary-blue);
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                ">Guardar Nota</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Eventos del modal
    modal.querySelector('.btn-cancelar').addEventListener('click', () => {
        document.body.removeChild(modal);
    });
    
    modal.querySelector('.btn-guardar').addEventListener('click', () => {
        const tipo = modal.querySelector('#tipoNota').value;
        const texto = modal.querySelector('#textoNota').value.trim();
        
        if (!texto) {
            alert('Por favor escriba una nota.');
            return;
        }
        
        agregarNotaAlPaciente(tipo, texto);
        document.body.removeChild(modal);
    });
    
    // Cerrar al hacer clic fuera del modal
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
}

function agregarNotaAlPaciente(tipo, texto) {
    const iconos = {
        'observacion': '📋',
        'recomendacion': '💡',
        'alerta': '⚠️',
        'mejora': '📈'
    };
    
    const colores = {
        'observacion': '#d1edff',
        'recomendacion': '#d1edff', 
        'alerta': '#fff3cd',
        'mejora': '#d4edda'
    };
    
    const borderColors = {
        'observacion': 'var(--secondary-blue)',
        'recomendacion': 'var(--secondary-blue)',
        'alerta': 'var(--medium-criticality)',
        'mejora': 'var(--positive-change)'
    };
    
    const titles = {
        'observacion': 'Observación',
        'recomendacion': 'Recomendación',
        'alerta': 'Atención',
        'mejora': 'Mejora'
    };
    
    const fecha = new Date().toLocaleDateString('es-ES');
    const hora = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    
    const nuevaNota = document.createElement('div');
    nuevaNota.style.cssText = `
        background: ${colores[tipo]};
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
        border-left: 4px solid ${borderColors[tipo]};
        animation: slideIn 0.3s ease;
    `;
    
    nuevaNota.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
            <strong>${iconos[tipo]} ${titles[tipo]}:</strong>
            <span style="font-size: 12px; color: var(--text-gray);">${fecha} ${hora}</span>
        </div>
        <div>${texto}</div>
        <div style="margin-top: 8px; font-size: 12px; color: var(--text-gray);">
            Dr. José Pérez - Cardiólogo
        </div>
    `;
    
    const notasContainer = document.getElementById('notasContainer');
    notasContainer.insertBefore(nuevaNota, notasContainer.firstChild);
    
    // Mostrar notificación de éxito
    mostrarNotificacion('Nota agregada correctamente', 'success');
    
    console.log(`Nueva nota agregada: ${tipo} - ${texto.substring(0, 50)}...`);
}

function mostrarNotificacion(mensaje, tipo) {
    const notificacion = document.createElement('div');
    notificacion.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        z-index: 1001;
        animation: slideIn 0.3s ease;
    `;
    
    if (tipo === 'success') {
        notificacion.style.background = 'var(--positive-change)';
        notificacion.innerHTML = `<i class="fas fa-check-circle"></i> ${mensaje}`;
    } else if (tipo === 'error') {
        notificacion.style.background = 'var(--high-criticality)';
        notificacion.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${mensaje}`;
    }
    
    document.body.appendChild(notificacion);
    
    setTimeout(() => {
        if (notificacion.parentElement) {
            notificacion.remove();
        }
    }, 4000);
}

// Añadir estilos de animación
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
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
`;
document.head.appendChild(style);