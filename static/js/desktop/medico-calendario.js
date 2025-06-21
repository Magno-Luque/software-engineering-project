// static/js/desktop/medico-calendario.js
document.addEventListener('DOMContentLoaded', () => {
    console.log('Calendario médico cargado.');
    
    // Inicializar calendario
    initCalendario();
    generarCalendarioMensual();
    generarCalendarioSemanal();
    
    // Establecer fecha de hoy por defecto
    const hoy = new Date();
    setFechaActual(hoy);
});

// Variables globales
let fechaActual = new Date();
let vistaActual = 'mensual';

// Datos simulados de citas
const citasSimuladas = {
    '2024-05-31': [
        {
            id: 'cita-001',
            paciente: 'Juan Pérez García',
            tipo: 'Consulta Cardiológica',
            hora: '10:00',
            duracion: 30,
            modalidad: 'presencial',
            estado: 'urgente',
            notas: 'Paciente con alerta crítica de glucosa'
        },
        {
            id: 'cita-002',
            paciente: 'María Elena González',
            tipo: 'Seguimiento Diabetes',
            hora: '11:30',
            duracion: 45,
            modalidad: 'virtual',
            estado: 'normal',
            zoomLink: 'https://zoom.us/j/123456789'
        },
        {
            id: 'cita-003',
            paciente: 'Carlos Alberto Rodríguez',
            tipo: 'Control Hipertensión',
            hora: '14:00',
            duracion: 30,
            modalidad: 'presencial',
            estado: 'normal'
        }
    ],
    '2024-06-01': [
        {
            id: 'cita-004',
            paciente: 'Ana María López',
            tipo: 'Primera Consulta',
            hora: '09:00',
            duracion: 60,
            modalidad: 'presencial',
            estado: 'normal'
        }
    ]
};

function initCalendario() {
    // Event listeners para navegación
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft' && e.ctrlKey) {
            cambiarMes(-1);
        } else if (e.key === 'ArrowRight' && e.ctrlKey) {
            cambiarMes(1);
        }
    });
    
    // Configurar fecha por defecto en modal
    const fechaInput = document.getElementById('cita-fecha');
    const hoy = new Date().toISOString().split('T')[0];
    fechaInput.value = hoy;
    fechaInput.min = hoy; // No permitir fechas pasadas
}

function cambiarVista(vista) {
    vistaActual = vista;
    
    // Actualizar botones
    document.querySelectorAll('.btn-calendario').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`btn-${vista}`).classList.add('active');
    
    // Mostrar/ocultar vistas
    document.getElementById('vista-mensual').style.display = vista === 'mensual' ? 'block' : 'none';
    document.getElementById('vista-semanal').style.display = vista === 'semanal' ? 'block' : 'none';
    
    if (vista === 'semanal') {
        generarCalendarioSemanal();
    }
}

function cambiarMes(direccion) {
    fechaActual.setMonth(fechaActual.getMonth() + direccion);
    actualizarCalendario();
}

function hoy() {
    fechaActual = new Date();
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
        `${meses[fechaActual.getMonth()]} ${fechaActual.getFullYear()}`;
    
    // Regenerar calendario
    if (vistaActual === 'mensual') {
        generarCalendarioMensual();
    } else {
        generarCalendarioSemanal();
    }
}

function generarCalendarioMensual() {
    const grid = document.getElementById('calendario-grid');
    grid.innerHTML = '';
    
    const primerDia = new Date(fechaActual.getFullYear(), fechaActual.getMonth(), 1);
    const ultimoDia = new Date(fechaActual.getFullYear(), fechaActual.getMonth() + 1, 0);
    
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
        const fecha = new Date(fechaActual.getFullYear(), fechaActual.getMonth(), dia);
        const diaDiv = crearDiaCalendario(fecha, false);
        grid.appendChild(diaDiv);
    }
    
    // Días del mes siguiente para completar la grilla
    const diasRestantes = 42 - (primerDiaSemana + ultimoDia.getDate());
    for (let dia = 1; dia <= diasRestantes; dia++) {
        const fecha = new Date(fechaActual.getFullYear(), fechaActual.getMonth() + 1, dia);
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
    const citasDelDia = citasSimuladas[fechaStr] || [];
    const citasContainer = diaDiv.querySelector('.dia-citas');
    
    citasDelDia.forEach(cita => {
        const citaElement = document.createElement('div');
        citaElement.className = `cita-calendario ${cita.modalidad} ${cita.estado}`;
        citaElement.innerHTML = `
            <span class="cita-hora-mini">${cita.hora}</span>
            <span class="cita-paciente-mini">${cita.paciente.split(' ')[0]}</span>
        `;
        citaElement.onclick = () => verDetallesCita(cita.id);
        citasContainer.appendChild(citaElement);
    });
    
    // Click en el día
    diaDiv.onclick = () => seleccionarDia(fecha);
    
    return diaDiv;
}

function generarCalendarioSemanal() {
    const grid = document.getElementById('semanal-grid');
    grid.innerHTML = '';
    
    // Obtener el lunes de la semana actual
    const inicioSemana = new Date(fechaActual);
    const dia = inicioSemana.getDay();
    const diff = inicioSemana.getDate() - dia + (dia === 0 ? -6 : 1);
    inicioSemana.setDate(diff);
    
    // Actualizar headers de días
    const headers = document.querySelectorAll('.dia-semanal-header');
    for (let i = 0; i < 7; i++) {
        const fecha = new Date(inicioSemana);
        fecha.setDate(fecha.getDate() + i);
        const nombresDias = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
        headers[i].textContent = `${nombresDias[i]} ${fecha.getDate()}`;
    }
    
    // Generar horas (8:00 a 18:00)
    for (let hora = 8; hora <= 18; hora++) {
        const filaHora = document.createElement('div');
        filaHora.className = 'semanal-fila';
        
        // Celda de hora
        const celdaHora = document.createElement('div');
        celdaHora.className = 'semanal-hora';
        celdaHora.textContent = `${hora.toString().padStart(2, '0')}:00`;
        filaHora.appendChild(celdaHora);
        
        // Celdas para cada día
        for (let dia = 0; dia < 7; dia++) {
            const celdaDia = document.createElement('div');
            celdaDia.className = 'semanal-celda';
            
            // Verificar si hay citas en esta hora
            const fecha = new Date(inicioSemana);
            fecha.setDate(fecha.getDate() + dia);
            const fechaStr = fecha.toISOString().split('T')[0];
            const citasDelDia = citasSimuladas[fechaStr] || [];
            
            const citaEnHora = citasDelDia.find(cita => {
                const horaCita = parseInt(cita.hora.split(':')[0]);
                return horaCita === hora;
            });
            
            if (citaEnHora) {
                celdaDia.className += ` ocupado ${citaEnHora.modalidad}`;
                celdaDia.innerHTML = `
                    <div class="cita-semanal">
                        <div class="cita-tiempo">${citaEnHora.hora}</div>
                        <div class="cita-paciente-semanal">${citaEnHora.paciente.split(' ')[0]} ${citaEnHora.paciente.split(' ')[1]}</div>
                        <div class="cita-tipo-semanal">${citaEnHora.tipo}</div>
                    </div>
                `;
                celdaDia.onclick = () => verDetallesCita(citaEnHora.id);
            } else {
                celdaDia.onclick = () => agendarEnHorario(`${hora}:00`, fechaStr);
                celdaDia.title = 'Click para agendar cita';
            }
            
            filaHora.appendChild(celdaDia);
        }
        
        grid.appendChild(filaHora);
    }
}

function seleccionarDia(fecha) {
    const fechaStr = fecha.toISOString().split('T')[0];
    const citasDelDia = citasSimuladas[fechaStr] || [];
    
    // Actualizar título del día seleccionado
    const diasSemana = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
    const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    
    document.getElementById('dia-seleccionado').textContent = 
        `${diasSemana[fecha.getDay()]}, ${fecha.getDate()} de ${meses[fecha.getMonth()]}`;
    
    // Actualizar lista de citas
    actualizarCitasDelDia(citasDelDia);
    
    // Marcar día seleccionado en calendario
    document.querySelectorAll('.calendario-dia').forEach(dia => {
        dia.classList.remove('seleccionado');
    });
    
    const diaSeleccionado = document.querySelector(`#citas-${fechaStr}`);
    if (diaSeleccionado) {
        diaSeleccionado.parentElement.classList.add('seleccionado');
    }
}

function actualizarCitasDelDia(citas) {
    const container = document.getElementById('citas-del-dia');
    container.innerHTML = '';
    
    if (citas.length === 0) {
        container.innerHTML = `
            <div class="sin-citas">
                <i class="fas fa-calendar-plus" style="font-size: 48px; color: var(--text-gray); opacity: 0.3; margin-bottom: 10px;"></i>
                <p>No hay citas programadas para este día</p>
                <button class="btn btn-primary" onclick="nuevaCita()">
                    <i class="fas fa-plus"></i> Agendar Cita
                </button>
            </div>
        `;
        return;
    }
    
    // Ordenar citas por hora
    citas.sort((a, b) => a.hora.localeCompare(b.hora));
    
    citas.forEach(cita => {
        const citaElement = document.createElement('div');
        citaElement.className = `cita-item ${cita.modalidad}`;
        
        let estadoIcon = '✅';
        let estadoClass = 'normal';
        let estadoText = 'Paciente estable';
        
        if (cita.estado === 'urgente') {
            estadoIcon = '⚠️';
            estadoClass = 'urgente';
            estadoText = 'Paciente con alerta crítica';
        } else if (cita.modalidad === 'virtual') {
            estadoIcon = '💻';
            estadoClass = 'virtual';
            estadoText = 'Enlace Zoom disponible';
        }
        
        citaElement.innerHTML = `
            <div class="cita-hora">${cita.hora}</div>
            <div class="cita-detalles">
                <div class="cita-paciente">${cita.paciente}</div>
                <div class="cita-tipo">${cita.tipo}</div>
                <div class="cita-estado ${estadoClass}">${estadoIcon} ${estadoText}</div>
            </div>
            <div class="cita-acciones">
                ${cita.modalidad === 'virtual' ? 
                    `<button class="btn-cita-accion btn-zoom" onclick="abrirZoom('${cita.zoomLink || '#'}')" title="Iniciar Zoom">
                        <i class="fas fa-video"></i>
                    </button>` : ''
                }
                <button class="btn-cita-accion" onclick="verDetallesCita('${cita.id}')" title="Ver detalles">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn-cita-accion" onclick="reprogramarCita('${cita.id}')" title="Reprogramar">
                    <i class="fas fa-clock"></i>
                </button>
            </div>
        `;
        
        container.appendChild(citaElement);
    });
    
    // Agregar horarios disponibles
    const horariosLibres = generarHorariosLibres(citas);
    if (horariosLibres.length > 0) {
        const libresContainer = document.createElement('div');
        libresContainer.className = 'horario-libre';
        
        horariosLibres.forEach(horario => {
            const horarioElement = document.createElement('div');
            horarioElement.className = 'horario-disponible';
            horarioElement.innerHTML = `
                <i class="fas fa-plus-circle"></i>
                <span>${horario} Disponible</span>
                <button class="btn-agendar" onclick="agendarEnHorario('${horario}')">Agendar</button>
            `;
            libresContainer.appendChild(horarioElement);
        });
        
        container.appendChild(libresContainer);
    }
}

function generarHorariosLibres(citasOcupadas) {
    const horariosDisponibles = [
        '08:00', '08:30', '09:00', '09:30', '10:00', '10:30',
        '11:00', '11:30', '14:00', '14:30', '15:00', '15:30',
        '16:00', '16:30', '17:00'
    ];
    
    const horariosOcupados = citasOcupadas.map(cita => cita.hora);
    const libres = horariosDisponibles.filter(horario => !horariosOcupados.includes(horario));
    
    // Mostrar solo los primeros 3 horarios libres
    return libres.slice(0, 3);
}

function nuevaCita() {
    document.getElementById('modal-nueva-cita').style.display = 'flex';
    
    // Limpiar formulario
    document.getElementById('form-nueva-cita').reset();
    
    // Establecer fecha actual por defecto
    const hoy = new Date().toISOString().split('T')[0];
    document.getElementById('cita-fecha').value = hoy;
}

function cerrarModalCita() {
    document.getElementById('modal-nueva-cita').style.display = 'none';
}

function guardarCita() {
    const form = document.getElementById('form-nueva-cita');
    const formData = new FormData(form);
    
    // Validación básica
    const paciente = document.getElementById('cita-paciente').value;
    const tipo = document.getElementById('cita-tipo').value;
    const fecha = document.getElementById('cita-fecha').value;
    const hora = document.getElementById('cita-hora').value;
    const modalidad = document.getElementById('cita-modalidad').value;
    
    if (!paciente || !tipo || !fecha || !hora || !modalidad) {
        alert('Por favor, complete todos los campos obligatorios.');
        return;
    }
    
    // Verificar disponibilidad
    const citasDelDia = citasSimuladas[fecha] || [];
    const horaOcupada = citasDelDia.find(cita => cita.hora === hora);
    
    if (horaOcupada) {
        alert(`Ya hay una cita programada a las ${hora}. Por favor, seleccione otro horario.`);
        return;
    }
    
    // Crear nueva cita
    const nuevaCita = {
        id: `cita-${Date.now()}`,
        paciente: document.getElementById('cita-paciente').selectedOptions[0].text,
        tipo: tipo,
        hora: hora,
        duracion: parseInt(document.getElementById('cita-duracion').value),
        modalidad: modalidad,
        estado: 'normal',
        notas: document.getElementById('cita-notas').value
    };
    
    if (modalidad === 'virtual') {
        nuevaCita.zoomLink = `https://zoom.us/j/${Math.random().toString().substr(2, 9)}`;
    }
    
    // Agregar a datos simulados
    if (!citasSimuladas[fecha]) {
        citasSimuladas[fecha] = [];
    }
    citasSimuladas[fecha].push(nuevaCita);
    
    console.log('Nueva cita creada:', nuevaCita);
    
    // Actualizar calendario
    actualizarCalendario();
    
    // Cerrar modal
    cerrarModalCita();
    
    // Mostrar confirmación
    alert(`Cita programada exitosamente:\n\nPaciente: ${nuevaCita.paciente}\nFecha: ${fecha}\nHora: ${hora}\nModalidad: ${modalidad === 'virtual' ? 'Virtual (Zoom)' : 'Presencial'}`);
}

function agendarEnHorario(hora, fecha = null) {
    nuevaCita();
    
    // Precargar hora y fecha si se proporcionan
    if (hora) {
        document.getElementById('cita-hora').value = hora;
    }
    
    if (fecha) {
        document.getElementById('cita-fecha').value = fecha;
    }
}

function verDetallesCita(citaId) {
    // Buscar la cita en los datos simulados
    let citaEncontrada = null;
    
    for (const fecha in citasSimuladas) {
        citaEncontrada = citasSimuladas[fecha].find(cita => cita.id === citaId);
        if (citaEncontrada) {
            citaEncontrada.fecha = fecha;
            break;
        }
    }
    
    if (!citaEncontrada) {
        alert('No se pudo encontrar la información de la cita.');
        return;
    }
    
    // Actualizar contenido del modal
    document.getElementById('detalle-titulo').textContent = `Cita - ${citaEncontrada.paciente}`;
    
    const detalleInfo = document.getElementById('detalle-cita-info');
    detalleInfo.innerHTML = `
        <div class="detalle-grid">
            <div class="detalle-item">
                <label>Paciente:</label>
                <span>${citaEncontrada.paciente}</span>
            </div>
            <div class="detalle-item">
                <label>Tipo de Consulta:</label>
                <span>${citaEncontrada.tipo}</span>
            </div>
            <div class="detalle-item">
                <label>Fecha:</label>
                <span>${new Date(citaEncontrada.fecha).toLocaleDateString('es-PE')}</span>
            </div>
            <div class="detalle-item">
                <label>Hora:</label>
                <span>${citaEncontrada.hora}</span>
            </div>
            <div class="detalle-item">
                <label>Duración:</label>
                <span>${citaEncontrada.duracion} minutos</span>
            </div>
            <div class="detalle-item">
                <label>Modalidad:</label>
                <span class="modalidad-badge ${citaEncontrada.modalidad}">
                    ${citaEncontrada.modalidad === 'virtual' ? '💻 Virtual (Zoom)' : '🏥 Presencial'}
                </span>
            </div>
            ${citaEncontrada.zoomLink ? `
                <div class="detalle-item zoom-link">
                    <label>Enlace Zoom:</label>
                    <button class="btn-zoom-link" onclick="abrirZoom('${citaEncontrada.zoomLink}')">
                        <i class="fas fa-video"></i> Iniciar Reunión
                    </button>
                </div>
            ` : ''}
            ${citaEncontrada.notas ? `
                <div class="detalle-item notas">
                    <label>Notas:</label>
                    <p>${citaEncontrada.notas}</p>
                </div>
            ` : ''}
        </div>
    `;
    
    // Mostrar modal
    document.getElementById('modal-detalle-cita').style.display = 'flex';
    
    // Guardar ID de cita actual para edición
    window.citaActualId = citaId;
}

function cerrarDetallesCita() {
    document.getElementById('modal-detalle-cita').style.display = 'none';
}

function editarCita() {
    // Cerrar modal de detalles y abrir modal de edición
    cerrarDetallesCita();
    
    // Aquí se abriría el modal de edición con los datos precargados
    alert('Funcionalidad de edición en desarrollo.\n\nPermitirá modificar:\n- Fecha y hora\n- Tipo de consulta\n- Modalidad\n- Notas');
}

function reprogramarCita(citaId) {
    if (confirm('¿Está seguro de que desea reprogramar esta cita?')) {
        alert('Funcionalidad de reprogramación en desarrollo.\n\nPermitirá:\n- Seleccionar nueva fecha\n- Elegir nuevo horario\n- Notificar al paciente');
    }
}

function abrirZoom(zoomLink) {
    if (zoomLink && zoomLink !== '#') {
        console.log('Abriendo Zoom:', zoomLink);
        
        // Confirmar antes de abrir
        if (confirm('¿Iniciar la consulta virtual por Zoom?')) {
            // Abrir en nueva ventana/pestaña
            window.open(zoomLink, '_blank');
            
            // En una aplicación real, también podrías:
            // - Registrar el inicio de la consulta
            // - Actualizar el estado de la cita
            // - Notificar al paciente
        }
    } else {
        alert('Enlace de Zoom no disponible.');
    }
}

function setFechaActual(fecha) {
    fechaActual = new Date(fecha);
    actualizarCalendario();
    seleccionarDia(fecha);
}

// Cerrar modales al hacer clic fuera
document.addEventListener('click', (e) => {
    const modales = ['modal-nueva-cita', 'modal-detalle-cita'];
    
    modales.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
});

// Cerrar modales con ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const modales = ['modal-nueva-cita', 'modal-detalle-cita'];
        
        modales.forEach(modalId => {
            const modal = document.getElementById(modalId);
            if (modal.style.display === 'flex') {
                modal.style.display = 'none';
            }
        });
    }
});