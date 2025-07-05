// static/js/desktop/medico-calendario-simple.js
document.addEventListener('DOMContentLoaded', () => {
    console.log('Calendario médico (solo lectura) cargado.');
    
    // Inicializar calendario
    initCalendarioSimple();
    generarCalendarioMensual();
    
    // Establecer fecha actual
    if (typeof fechaActual !== 'undefined') {
        setFechaActual(fechaActual);
    } else {
        setFechaActual(new Date());
    }
});

// Variables globales
let fechaCalendario = new Date();
let citasData = typeof citasMedico !== 'undefined' ? citasMedico : [];

function initCalendarioSimple() {
    console.log('Iniciando calendario simple para médico');
    console.log('Citas cargadas:', citasData.length);
}

function cambiarMes(direccion) {
    fechaCalendario.setMonth(fechaCalendario.getMonth() + direccion);
    actualizarCalendario();
}

function irAHoy() {
    fechaCalendario = new Date();
    actualizarCalendario();
    seleccionarDia(new Date());
}

function actualizarCalendario() {
    // Actualizar título del mes
    const meses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];
    
    document.getElementById('mes-actual').textContent = 
        `${meses[fechaCalendario.getMonth()]} ${fechaCalendario.getFullYear()}`;
    
    // Regenerar calendario
    generarCalendarioMensual();
}

function generarCalendarioMensual() {
    const grid = document.getElementById('calendario-grid');
    if (!grid) return;
    
    grid.innerHTML = '';
    
    const primerDia = new Date(fechaCalendario.getFullYear(), fechaCalendario.getMonth(), 1);
    const ultimoDia = new Date(fechaCalendario.getFullYear(), fechaCalendario.getMonth() + 1, 0);
    
    // Ajustar primer día (Lunes = 0)
    let primerDiaSemana = primerDia.getDay();
    primerDiaSemana = primerDiaSemana === 0 ? 6 : primerDiaSemana - 1;
    
    // Días del mes anterior
    for (let i = primerDiaSemana - 1; i >= 0; i--) {
        const dia = new Date(primerDia);
        dia.setDate(dia.getDate() - (i + 1));
        const diaDiv = crearDiaCalendario(dia, true);
        grid.appendChild(diaDiv);
    }
    
    // Días del mes actual
    for (let dia = 1; dia <= ultimoDia.getDate(); dia++) {
        const fecha = new Date(fechaCalendario.getFullYear(), fechaCalendario.getMonth(), dia);
        const diaDiv = crearDiaCalendario(fecha, false);
        grid.appendChild(diaDiv);
    }
    
    // Días del mes siguiente para completar la grilla
    const diasRestantes = 42 - (primerDiaSemana + ultimoDia.getDate());
    for (let dia = 1; dia <= diasRestantes; dia++) {
        const fecha = new Date(fechaCalendario.getFullYear(), fechaCalendario.getMonth() + 1, dia);
        const diaDiv = crearDiaCalendario(fecha, true);
        grid.appendChild(diaDiv);
    }
}

function crearDiaCalendario(fecha, otroMes) {
    const diaDiv = document.createElement('div');
    diaDiv.className = `calendario-dia ${otroMes ? 'otro-mes' : ''}`;
    
    const fechaStr = fecha.toISOString().split('T')[0];
    const esHoy = fechaStr === new Date().toISOString().split('T')[0];
    
    if (esHoy) {
        diaDiv.classList.add('hoy');
    }
    
    diaDiv.innerHTML = `
        <div class="dia-numero">${fecha.getDate()}</div>
        <div class="dia-citas" id="citas-${fechaStr}"></div>
    `;
    
    // Agregar citas del día
    const citasDelDia = obtenerCitasDelDia(fechaStr);
    const citasContainer = diaDiv.querySelector('.dia-citas');
    
    citasDelDia.forEach(cita => {
        const citaElement = document.createElement('div');
        citaElement.className = `cita-calendario ${cita.tipo.toLowerCase()} ${cita.estado.toLowerCase()}`;
        citaElement.innerHTML = `
            <span class="cita-hora-mini">${cita.hora_inicio}</span>
            <span class="cita-paciente-mini">${cita.paciente_nombre.split(' ')[0]}</span>
        `;
        citaElement.onclick = () => verDetallesCita(cita.id);
        citaElement.title = `${cita.hora_inicio} - ${cita.paciente_nombre} (${cita.tipo})`;
        citasContainer.appendChild(citaElement);
    });
    
    // Click en el día
    diaDiv.onclick = () => seleccionarDia(fecha);
    
    return diaDiv;
}

function obtenerCitasDelDia(fechaStr) {
    return citasData.filter(cita => {
        // Convertir fecha de cita a string para comparar
        const fechaCita = new Date(cita.fecha_cita).toISOString().split('T')[0];
        return fechaCita === fechaStr;
    });
}

function seleccionarDia(fecha) {
    const fechaStr = fecha.toISOString().split('T')[0];
    const citasDelDia = obtenerCitasDelDia(fechaStr);
    
    // Actualizar título del día seleccionado
    const diasSemana = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
    const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    
    document.getElementById('dia-seleccionado').textContent = 
        `${diasSemana[fecha.getDay()]}, ${fecha.getDate()} de ${meses[fecha.getMonth()]}`;
    
    // Actualizar lista de citas
    mostrarCitasDelDia(citasDelDia);
    
    // Marcar día seleccionado en calendario
    document.querySelectorAll('.calendario-dia').forEach(dia => {
        dia.classList.remove('seleccionado');
    });
    
    const diaSeleccionado = document.querySelector(`#citas-${fechaStr}`);
    if (diaSeleccionado) {
        diaSeleccionado.parentElement.classList.add('seleccionado');
    }
}

function mostrarCitasDelDia(citas) {
    const container = document.getElementById('citas-del-dia');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (citas.length === 0) {
        container.innerHTML = `
            <div class="sin-citas">
                <i class="fas fa-calendar" style="font-size: 48px; color: var(--text-gray); opacity: 0.3; margin-bottom: 10px;"></i>
                <p>No hay citas programadas para este día</p>
            </div>
        `;
        return;
    }
    
    // Ordenar citas por hora
    citas.sort((a, b) => a.hora_inicio.localeCompare(b.hora_inicio));
    
    citas.forEach(cita => {
        const citaElement = document.createElement('div');
        citaElement.className = `cita-item ${cita.tipo.toLowerCase()} ${cita.estado.toLowerCase()}`;
        
        let estadoIcon = '';
        let estadoClass = '';
        let estadoText = '';
        
        switch (cita.estado) {
            case 'AGENDADA':
                estadoIcon = '📅';
                estadoClass = 'agendada';
                estadoText = 'Cita programada';
                break;
            case 'ATENDIDA':
                estadoIcon = '✅';
                estadoClass = 'atendida';
                estadoText = 'Cita atendida';
                break;
            case 'CANCELADA':
                estadoIcon = '❌';
                estadoClass = 'cancelada';
                estadoText = 'Cita cancelada';
                break;
            case 'NO_ATENDIDA':
                estadoIcon = '⚠️';
                estadoClass = 'no-atendida';
                estadoText = 'Paciente no asistió';
                break;
        }
        
        if (cita.tipo === 'VIRTUAL') {
            estadoIcon = '💻';
            estadoText += ' (Virtual)';
        }
        
        citaElement.innerHTML = `
            <div class="cita-hora">${cita.hora_inicio}</div>
            <div class="cita-detalles">
                <div class="cita-paciente">${cita.paciente_nombre}</div>
                <div class="cita-tipo">${cita.especialidad}</div>
                <div class="cita-estado ${estadoClass}">${estadoIcon} ${estadoText}</div>
                ${cita.motivo_consulta ? `<div class="cita-motivo">${cita.motivo_consulta}</div>` : ''}
            </div>
            <div class="cita-acciones">
                <button class="btn-cita-accion" onclick="verDetallesCita('${cita.id}')" title="Ver detalles">
                    <i class="fas fa-eye"></i>
                </button>
                ${cita.tipo === 'VIRTUAL' && cita.enlace_virtual ? 
                    `<button class="btn-cita-accion btn-virtual" onclick="abrirEnlaceVirtual('${cita.enlace_virtual}')" title="Unirse a videollamada">
                        <i class="fas fa-video"></i>
                    </button>` : ''
                }
            </div>
        `;
        
        container.appendChild(citaElement);
    });
}

function verDetallesCita(citaId) {
    // Buscar la cita en los datos
    const cita = citasData.find(c => c.id == citaId);
    
    if (!cita) {
        alert('No se pudo encontrar la información de la cita.');
        return;
    }
    
    // Actualizar contenido del modal
    document.getElementById('detalle-titulo').textContent = `Cita - ${cita.paciente_nombre}`;
    
    const detalleInfo = document.getElementById('detalle-cita-info');
    detalleInfo.innerHTML = `
        <div class="detalle-grid">
            <div class="detalle-item">
                <label>Paciente:</label>
                <span>${cita.paciente_nombre}</span>
            </div>
            <div class="detalle-item">
                <label>Especialidad:</label>
                <span>${cita.especialidad}</span>
            </div>
            <div class="detalle-item">
                <label>Fecha:</label>
                <span>${new Date(cita.fecha_cita).toLocaleDateString('es-PE')}</span>
            </div>
            <div class="detalle-item">
                <label>Hora:</label>
                <span>${cita.hora_inicio} - ${cita.hora_fin}</span>
            </div>
            <div class="detalle-item">
                <label>Duración:</label>
                <span>${cita.duracion_minutos} minutos</span>
            </div>
            <div class="detalle-item">
                <label>Tipo:</label>
                <span class="tipo-badge ${cita.tipo.toLowerCase()}">
                    ${cita.tipo === 'VIRTUAL' ? '💻 Virtual' : '🏥 Presencial'}
                </span>
            </div>
            <div class="detalle-item">
                <label>Estado:</label>
                <span class="estado-badge ${cita.estado.toLowerCase()}">${cita.estado}</span>
            </div>
            ${cita.consultorio ? `
                <div class="detalle-item">
                    <label>Consultorio:</label>
                    <span>${cita.consultorio}</span>
                </div>
            ` : ''}
            ${cita.enlace_virtual ? `
                <div class="detalle-item enlace-virtual">
                    <label>Enlace Virtual:</label>
                    <button class="btn-enlace-virtual" onclick="abrirEnlaceVirtual('${cita.enlace_virtual}')">
                        <i class="fas fa-video"></i> Unirse a la videollamada
                    </button>
                </div>
            ` : ''}
            ${cita.motivo_consulta ? `
                <div class="detalle-item motivo">
                    <label>Motivo de consulta:</label>
                    <p>${cita.motivo_consulta}</p>
                </div>
            ` : ''}
            ${cita.observaciones ? `
                <div class="detalle-item observaciones">
                    <label>Observaciones:</label>
                    <p>${cita.observaciones}</p>
                </div>
            ` : ''}
        </div>
    `;
    
    // Mostrar modal
    document.getElementById('modal-detalle-cita').style.display = 'flex';
}

function cerrarDetallesCita() {
    document.getElementById('modal-detalle-cita').style.display = 'none';
}

function abrirEnlaceVirtual(enlace) {
    if (enlace && enlace !== '#') {
        if (confirm('¿Unirse a la consulta virtual?')) {
            window.open(enlace, '_blank');
        }
    } else {
        alert('Enlace virtual no disponible.');
    }
}

function setFechaActual(fecha) {
    fechaCalendario = new Date(fecha);
    actualizarCalendario();
    seleccionarDia(fecha);
}

// Cerrar modal al hacer clic fuera
document.addEventListener('click', (e) => {
    const modal = document.getElementById('modal-detalle-cita');
    if (e.target === modal) {
        cerrarDetallesCita();
    }
});

// Cerrar modal con ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        cerrarDetallesCita();
    }
});