// static/js/desktop/citas.js - JavaScript simple para citas

let enfermedadSeleccionada = null;
let horarioSeleccionado = null;

document.addEventListener('DOMContentLoaded', function() {
    cargarEnfermedades();
    
    // Evento para habilitar botón buscar
    document.getElementById('enfermedadSelect').addEventListener('change', function() {
        const btnBuscar = document.getElementById('btnBuscar');
        if (this.value) {
            enfermedadSeleccionada = JSON.parse(this.value);
            btnBuscar.disabled = false;
        } else {
            btnBuscar.disabled = true;
        }
    });
});

async function cargarEnfermedades() {
    try {
        const response = await fetch('/paciente/citas/enfermedades');
        const data = await response.json();
        
        if (data.exito) {
            const select = document.getElementById('enfermedadSelect');
            data.enfermedades.forEach(enfermedad => {
                const option = document.createElement('option');
                option.value = JSON.stringify(enfermedad);
                option.textContent = `${enfermedad.codigo} - ${enfermedad.nombre}`;
                select.appendChild(option);
            });
        } else {
            mostrarError('Error al cargar enfermedades: ' + data.error);
        }
    } catch (error) {
        mostrarError('Error de conexión');
    }
}

async function buscarHorarios() {
    try {
        mostrarLoading();
        
        const fechaDesde = new Date().toISOString().split('T')[0];
        const fechaHasta = new Date(Date.now() + 30*24*60*60*1000).toISOString().split('T')[0];
        
        const response = await fetch(`/paciente/citas/horarios-disponibles?fecha_desde=${fechaDesde}&fecha_hasta=${fechaHasta}&especialidad=${enfermedadSeleccionada.especialidad_requerida}`);
        const data = await response.json();
        
        if (data.exito) {
            mostrarHorarios(data.horarios_por_fecha);
            mostrarPaso(2);
        } else {
            mostrarError('Error al cargar horarios: ' + data.error);
        }
    } catch (error) {
        mostrarError('Error de conexión');
    } finally {
        ocultarLoading();
    }
}

function mostrarHorarios(horariosPorFecha) {
    const container = document.getElementById('horariosContainer');
    container.innerHTML = '';
    
    if (Object.keys(horariosPorFecha).length === 0) {
        container.innerHTML = `
            <div class="no-horarios">
                <i class="fas fa-calendar-times"></i>
                <p>No hay horarios disponibles para esta enfermedad</p>
            </div>
        `;
        return;
    }
    
    const grid = document.createElement('div');
    grid.className = 'horarios-grid';
    
    Object.keys(horariosPorFecha).sort().forEach(fecha => {
        horariosPorFecha[fecha].forEach(horario => {
            // Solo mostrar horarios para la enfermedad seleccionada
            if (horario.enfermedad.id === enfermedadSeleccionada.id) {
                const item = crearHorarioItem(fecha, horario);
                grid.appendChild(item);
            }
        });
    });
    
    container.appendChild(grid);
}

function crearHorarioItem(fecha, horario) {
    const item = document.createElement('div');
    item.className = 'horario-item';
    item.onclick = () => seleccionarHorario(item, fecha, horario);
    
    const fechaObj = new Date(fecha);
    fechaObj.setDate(fechaObj.getDate() + 1); // Sumar 1 día
    
    const fechaFormateada = fechaObj.toLocaleDateString('es-ES', {
        weekday: 'long',
        day: 'numeric',
        month: 'long'
    });
    
    item.innerHTML = `
        <div class="horario-fecha">${fechaFormateada}</div>
        <div class="horario-hora">${horario.hora_inicio} - ${horario.hora_fin}</div>
        <div class="horario-medico">${horario.medico.nombre}</div>
        <div class="horario-medico">${horario.medico.especialidad}</div>
        <span class="horario-tipo ${horario.tipo}">${horario.tipo}</span>
        ${horario.consultorio ? `<div style="font-size: 0.8em; color: #666; margin-top: 5px;">${horario.consultorio}</div>` : ''}
    `;
    
    return item;
}

function seleccionarHorario(item, fecha, horario) {
    // Quitar selección anterior
    document.querySelectorAll('.horario-item').forEach(i => i.classList.remove('selected'));
    
    const fechaObj = new Date(fecha);
    fechaObj.setDate(fechaObj.getDate() + 1);
    const nuevaFecha = fechaObj.toISOString().split('T')[0];

    // Seleccionar este horario
    item.classList.add('selected');
    horarioSeleccionado = {
        ...horario,
        fecha: fecha
    };
    
    // Habilitar botón continuar
    document.getElementById('btnContinuar').disabled = false;
}

function mostrarFormulario() {
    const fechaObj = new Date(horarioSeleccionado.fecha);
    fechaObj.setDate(fechaObj.getDate() + 1); // Sumar 1 día

    const fechaFormateada = fechaObj.toLocaleDateString('es-ES', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
    
    document.getElementById('resumenCita').innerHTML = `
        <div class="resumen-item">
            <strong>Enfermedad:</strong> ${enfermedadSeleccionada.codigo} - ${enfermedadSeleccionada.nombre}
        </div>
        <div class="resumen-item">
            <strong>Médico:</strong> ${horarioSeleccionado.medico.nombre}
        </div>
        <div class="resumen-item">
            <strong>Fecha:</strong> ${fechaFormateada}
        </div>
        <div class="resumen-item">
            <strong>Horario:</strong> ${horarioSeleccionado.hora_inicio} - ${horarioSeleccionado.hora_fin}
        </div>
        <div class="resumen-item">
            <strong>Tipo:</strong> ${horarioSeleccionado.tipo}
            ${horarioSeleccionado.consultorio ? ` - ${horarioSeleccionado.consultorio}` : ''}
        </div>
    `;
    
    mostrarPaso(3);
}

async function agendarCita() {
    const motivo = document.getElementById('motivoConsulta').value.trim();
    const observaciones = document.getElementById('observaciones').value.trim();
    
    if (!motivo) {
        mostrarError('El motivo de la consulta es obligatorio');
        return;
    }
    
    try {
        const btnAgendar = document.getElementById('btnAgendar');
        btnAgendar.disabled = true;
        btnAgendar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Agendando...';
        
        const response = await fetch('/paciente/citas/crear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                horario_id: horarioSeleccionado.id,
                enfermedad_id: enfermedadSeleccionada.id,
                motivo_consulta: motivo,
                observaciones: observaciones
            })
        });
        
        const result = await response.json();
        
        if (result.exito) {
            mostrarConfirmacion(result);
            mostrarPaso(4);
        } else {
            mostrarError('Error al agendar: ' + result.error);
        }
    } catch (error) {
        mostrarError('Error de conexión');
    } finally {
        const btnAgendar = document.getElementById('btnAgendar');
        btnAgendar.disabled = false;
        btnAgendar.innerHTML = '<i class="fas fa-calendar-plus"></i> Agendar Cita';
    }
}

function mostrarConfirmacion(result) {
    const fechaObj = new Date(result.detalles.fecha);
    fechaObj.setDate(fechaObj.getDate() + 1); // Sumar 1 día

    const fechaFormateada = fechaObj.toLocaleDateString('es-ES', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
    
    document.getElementById('confirmacionCita').innerHTML = `
        <div class="alert alert-success">
            <strong>Cita #${result.cita_id} agendada exitosamente</strong>
        </div>
        <div class="resumen-item">
            <strong>Médico:</strong> ${result.detalles.medico}
        </div>
        <div class="resumen-item">
            <strong>Fecha:</strong> ${fechaFormateada}
        </div>
        <div class="resumen-item">
            <strong>Horario:</strong> ${result.detalles.hora_inicio} - ${result.detalles.hora_fin}
        </div>
        <div class="resumen-item">
            <strong>Tipo:</strong> ${result.detalles.tipo}
            ${result.detalles.consultorio ? ` - ${result.detalles.consultorio}` : ''}
        </div>
        ${result.detalles.enlace_virtual ? `
            <div class="resumen-item">
                <strong>Enlace Virtual:</strong> <a href="${result.detalles.enlace_virtual}" target="_blank">${result.detalles.enlace_virtual}</a>
            </div>
        ` : ''}
        <div class="alert alert-info" style="margin-top: 15px;">
            <strong>Importante:</strong> Llega 15 minutos antes. Si necesitas cancelar, hazlo con 2 horas de anticipación.
        </div>
    `;
}

function nuevaCita() {
    // Resetear variables
    enfermedadSeleccionada = null;
    horarioSeleccionado = null;
    
    // Resetear formulario
    document.getElementById('enfermedadSelect').value = '';
    document.getElementById('motivoConsulta').value = '';
    document.getElementById('observaciones').value = '';
    
    // Resetear botones
    document.getElementById('btnBuscar').disabled = true;
    document.getElementById('btnContinuar').disabled = true;
    
    // Mostrar paso 1
    mostrarPaso(1);
}

function volverPaso1() {
    mostrarPaso(1);
}

function volverPaso2() {
    mostrarPaso(2);
}

function mostrarPaso(paso) {
    // Ocultar todos los pasos
    for (let i = 1; i <= 4; i++) {
        document.getElementById(`paso${i}`).classList.add('hidden');
    }
    
    // Mostrar paso seleccionado
    document.getElementById(`paso${paso}`).classList.remove('hidden');
}

function mostrarLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function ocultarLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function mostrarError(mensaje) {
    const container = document.getElementById('alertContainer');
    container.innerHTML = `
        <div class="alert alert-error">
            <strong>Error:</strong> ${mensaje}
        </div>
    `;
    
    setTimeout(() => {
        container.innerHTML = '';
    }, 5000);
}

function mostrarExito(mensaje) {
    const container = document.getElementById('alertContainer');
    container.innerHTML = `
        <div class="alert alert-success">
            <strong>Éxito:</strong> ${mensaje}
        </div>
    `;
    
    setTimeout(() => {
        container.innerHTML = '';
    }, 5000);
}