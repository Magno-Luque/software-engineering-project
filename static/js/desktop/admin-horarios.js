// static/js/desktop/admin-horarios.js 
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sistema de Horarios Mejorado iniciado');

    // ========================
    // ELEMENTOS DEL DOM
    // ========================
    const nuevoHorarioBtn = document.getElementById('nuevoHorarioBtn');
    const semanaAnterior = document.getElementById('semanaAnterior');
    const semanaSiguiente = document.getElementById('semanaSiguiente');
    const periodoActual = document.getElementById('periodoActual');
    const modalHorario = document.getElementById('modalHorario');
    const closeHorarioModal = document.getElementById('closeHorarioModal');
    const cancelHorario = document.getElementById('cancelHorario');
    const guardarHorario = document.getElementById('guardarHorario');
    const formHorario = document.getElementById('formHorario');
    const calendarioBody = document.querySelector('.calendar-body');
    
    // Nuevos elementos
    const modalTitle = document.getElementById('modalTitle');
    const btnGuardarTexto = document.getElementById('btnGuardarTexto');
    const horarioInicio = document.getElementById('horarioInicio');
    const horarioFin = document.getElementById('horarioFin');
    const horarioTipo = document.getElementById('horarioTipo');
    const consultorioGroup = document.getElementById('consultorioGroup');
    const enlaceZoomGroup = document.getElementById('enlaceZoomGroup');
    const horarioConsultorio = document.getElementById('horarioConsultorio');
    const horarioEnlaceZoom = document.getElementById('horarioEnlaceZoom');

    // ========================
    // VARIABLES GLOBALES
    // ========================
    let fechaActual = new Date();
    let horariosActuales = [];
    let profesionalesDisponibles = [];
    let modoEdicion = false;
    let horarioEditandoId = null;

    // ========================
    // MAPEO DE HORAS PARA CÁLCULOS
    // ========================
    const horasDisponibles = [
        '08:00', '09:00', '10:00', '11:00', '12:00', 
        '13:00', '14:00', '15:00', '16:00', '17:00', 
        '18:00', '19:00', '20:00'
    ];

    // ========================
    // FUNCIONES DE UTILIDAD DE HORAS
    // ========================
    function calcularHoraFin(horaInicio) {
        const indice = horasDisponibles.indexOf(horaInicio);
        if (indice !== -1 && indice < horasDisponibles.length - 1) {
            return horasDisponibles[indice + 1];
        }
        return null;
    }

    function llenarSelectHoraFin(horaInicioSeleccionada) {
        // Limpiar opciones
        horarioFin.innerHTML = '<option value="">Seleccionar hora fin...</option>';
        
        if (!horaInicioSeleccionada) return;

        const indiceInicio = horasDisponibles.indexOf(horaInicioSeleccionada);
        
        // Llenar con horas posteriores
        for (let i = indiceInicio + 1; i < horasDisponibles.length; i++) {
            const hora = horasDisponibles[i];
            const option = document.createElement('option');
            option.value = hora;
            
            // Formato amigable
            const hora24 = parseInt(hora.split(':')[0]);
            const formato12 = hora24 > 12 ? `${hora24 - 12}:00 PM` : 
                            hora24 === 12 ? '12:00 PM' : `${hora24}:00 AM`;
            
            // NUEVO: Indicar si es slot individual o rango
            if (i === indiceInicio + 1) {
                option.textContent = `${formato12} (Slot individual de 1 hora)`;
            } else {
                const totalHoras = i - indiceInicio;
                option.textContent = `${formato12} (${totalHoras} slots de 1 hora)`;
            }
            
            horarioFin.appendChild(option);
        }

        // Auto-seleccionar la siguiente hora por defecto (slot individual)
        const horaFinAuto = calcularHoraFin(horaInicioSeleccionada);
        if (horaFinAuto) {
            horarioFin.value = horaFinAuto;
        }
    }

    function generarEnlaceZoom() {
        // Generar enlace ficticio único
        const meetingId = Math.floor(Math.random() * 900000000) + 100000000; // 9 dígitos
        const password = Math.floor(Math.random() * 900000) + 100000; // 6 dígitos
        return `https://zoom.us/j/${meetingId}?pwd=${password}`;
    }

    // ========================
    // EVENTOS DE CAMBIO EN FORMULARIO
    // ========================
    horarioInicio.addEventListener('change', function() {
        const horaSeleccionada = this.value;
        llenarSelectHoraFin(horaSeleccionada);
    });

    horarioTipo.addEventListener('change', function() {
        const tipo = this.value;
        manejarCambioTipoConsulta(tipo);
    });

    function manejarCambioTipoConsulta(tipo) {
        // Resetear visibilidad
        consultorioGroup.style.display = 'none';
        enlaceZoomGroup.style.display = 'none';
        horarioConsultorio.required = false;

        switch(tipo) {
            case 'presencial':
                consultorioGroup.style.display = 'block';
                horarioConsultorio.required = true;
                horarioEnlaceZoom.value = '';
                break;
                
            case 'virtual':
                enlaceZoomGroup.style.display = 'block';
                horarioEnlaceZoom.value = generarEnlaceZoom();
                horarioConsultorio.value = '';
                break;
                
            case 'mixto':
                consultorioGroup.style.display = 'block';
                enlaceZoomGroup.style.display = 'block';
                horarioConsultorio.required = true;
                horarioEnlaceZoom.value = generarEnlaceZoom();
                break;
                
            default:
                horarioEnlaceZoom.value = '';
                horarioConsultorio.value = '';
        }
    }

    // ========================
    // FUNCIONES PRINCIPALES (MANTENIDAS)
    // ========================
    
    function obtenerLunesDeLaSemana(fecha) {
        const dia = fecha.getDay();
        const diasHastaLunes = dia === 0 ? -6 : 1 - dia;
        const lunes = new Date(fecha);
        lunes.setDate(fecha.getDate() + diasHastaLunes);
        return lunes;
    }

    function formatearFecha(fecha) {
        return fecha.toISOString().split('T')[0];
    }

    function actualizarPeriodo() {
        const lunes = obtenerLunesDeLaSemana(fechaActual);
        const viernes = new Date(lunes);
        viernes.setDate(lunes.getDate() + 4);
        
        const opciones = { day: 'numeric', month: 'long' };
        const inicioTexto = lunes.toLocaleDateString('es-ES', opciones);
        const finTexto = viernes.toLocaleDateString('es-ES', opciones);
        const año = fechaActual.getFullYear();
        
        periodoActual.textContent = `Semana del ${inicioTexto} - ${finTexto}, ${año}`;
        
        actualizarFechasEnHeader(lunes);
        cargarHorariosSemana(formatearFecha(lunes));
    }

    function actualizarFechasEnHeader(lunes) {
        const columnasDias = document.querySelectorAll('.day-column');
        const nombresDias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'];
        
        columnasDias.forEach((columna, index) => {
            const fecha = new Date(lunes);
            fecha.setDate(lunes.getDate() + index);
            
            const nombreDia = columna.querySelector('.day-name');
            const fechaDia = columna.querySelector('.day-date');
            
            if (nombreDia && fechaDia) {
                nombreDia.textContent = nombresDias[index];
                fechaDia.textContent = fecha.toLocaleDateString('es-ES', { 
                    day: 'numeric', 
                    month: 'short' 
                });
            }
        });
    }

    // ==============
    // CARGA DE DATOS
    // ==============
    
    async function cargarProfesionalesActivos() {
        try {
            const response = await fetch('/admin/profesionales/activos');
            const data = await response.json();
            
            if (data.exito) {
                profesionalesDisponibles = data.profesionales;
                llenarSelectProfesionales();
            } else {
                console.error('Error al cargar profesionales:', data.error);
                mostrarError('Error al cargar lista de profesionales');
            }
        } catch (error) {
            console.error('Error:', error);
            mostrarError('Error de conexión al cargar profesionales');
        }
    }

    function llenarSelectProfesionales() {
        const select = document.getElementById('horarioProfesional');
        
        // Limpiar opciones existentes excepto la primera
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }
        
        // Agregar profesionales
        profesionalesDisponibles.forEach(prof => {
            const option = document.createElement('option');
            option.value = prof.id;
            option.textContent = `${prof.nombre_completo} - ${prof.especialidad}`;
            select.appendChild(option);
        });
    }
    
    // Mejora en la función cargarHorariosSemana para debugging
    async function cargarHorariosSemana(fechaLunes) {
        try {
            console.log(`Cargando horarios para semana del: ${fechaLunes}`);
            
            const response = await fetch(`/admin/horarios/semana?fecha=${fechaLunes}`);
            const data = await response.json();
            
            console.log('Respuesta del servidor:', data);
            
            if (data.exito) {
                horariosActuales = data.datos_dias;
                console.log('Datos de horarios procesados:', horariosActuales);
                renderizarCalendario(data.datos_dias);
            } else {
                console.error('Error en respuesta:', data.error);
                mostrarError('Error al cargar horarios: ' + data.error);
            }
            
        } catch (error) {
            console.error('Error en fetch:', error);
            mostrarError('Error de conexión al cargar horarios');
        } finally {
            hideLoading();
        }
    }

    function renderizarCalendario(datosHorarios) {
        // Limpiar calendario actual
        calendarioBody.innerHTML = '';
        
        // Crear filas por hora (usando las horas disponibles)
        horasDisponibles.forEach(hora => {
            const fila = crearFilaHorario(hora, datosHorarios);
            calendarioBody.appendChild(fila);
        });
    }

    function crearFilaHorario(hora, datosHorarios) {
        const fila = document.createElement('div');
        fila.className = 'time-row';
        
        // Columna de hora con formato amigable
        const columnaHora = document.createElement('div');
        columnaHora.className = 'time-slot';
        const hora24 = parseInt(hora.split(':')[0]);
        const formato12 = hora24 > 12 ? `${hora24 - 12}:00 PM` : 
                         hora24 === 12 ? '12:00 PM' : `${hora24}:00 AM`;
        columnaHora.textContent = formato12;
        fila.appendChild(columnaHora);
        
        // Columnas de días (Lunes a Viernes)
        const fechas = Object.keys(datosHorarios).sort();
        fechas.forEach(fecha => {
            const columnaDia = crearColumnaDia(hora, datosHorarios[fecha]);
            fila.appendChild(columnaDia);
        });
        
        return fila;
    }

    function crearColumnaDia(hora, datosDelDia) {
        const columna = document.createElement('div');
        columna.className = 'day-slot';
        
        console.log(`Creando columna para hora ${hora}, día:`, datosDelDia);
        
        // Buscar horario que coincida con esta hora
        const horarioEncontrado = datosDelDia.horarios.find(h => {
            const horaInicio = h.hora_inicio;
            const horaFin = h.hora_fin;
            
            console.log(`Comparando: ${hora} con rango ${horaInicio} - ${horaFin}`);
            
            // Convertir horas a minutos para comparación más precisa
            const horaActualMinutos = convertirHoraAMinutos(hora);
            const horaInicioMinutos = convertirHoraAMinutos(horaInicio);
            const horaFinMinutos = convertirHoraAMinutos(horaFin);
            
            // Un slot de hora está en el horario si la hora actual coincide exactamente con la hora de inicio
            // O si está dentro del rango del horario
            const coincide = horaActualMinutos >= horaInicioMinutos && horaActualMinutos < horaFinMinutos;
            
            console.log(`  Minutos: ${horaActualMinutos} >= ${horaInicioMinutos} && ${horaActualMinutos} < ${horaFinMinutos} = ${coincide}`);
            
            return coincide;
        });
        
        console.log('Horario encontrado:', horarioEncontrado);
        
        let slot;
        if (horarioEncontrado) {
            // Si hay horario disponible, verificar si está ocupado o libre
            if (horarioEncontrado.ocupado) {
                slot = crearSlotOcupado(horarioEncontrado);
            } else {
                slot = crearSlotDisponible(horarioEncontrado);
            }
        } else {
            // No hay horario definido para esta hora
            slot = crearSlotVacio();
        }
        
        // Agregar fecha como atributo para eventos
        if (datosDelDia.fecha instanceof Date) {
            slot.dataset.fecha = datosDelDia.fecha.toISOString().split('T')[0];
        } else {
            slot.dataset.fecha = datosDelDia.fecha;
        }
        slot.dataset.hora = hora;
        
        columna.appendChild(slot);
        return columna;
    }

    // Función auxiliar para convertir hora HH:MM a minutos
    function convertirHoraAMinutos(hora) {
        const [horas, minutos] = hora.split(':').map(Number);
        return horas * 60 + minutos;
    }

    function crearSlotOcupado(horario) {
        const slot = document.createElement('div');
        slot.className = `appointment-slot occupied`;
        slot.dataset.horarioId = horario.id;
        
        const nombreProfesional = document.createElement('span');
        nombreProfesional.className = 'professional-name';
        nombreProfesional.textContent = horario.medico_nombre;
        
        const tipoConsulta = document.createElement('span');
        tipoConsulta.className = 'appointment-type';
        tipoConsulta.textContent = horario.consultorio || horario.tipo;
        
        const estadoLabel = document.createElement('span');
        estadoLabel.className = 'status-label occupied';
        estadoLabel.textContent = 'OCUPADO';
        
        slot.appendChild(nombreProfesional);
        slot.appendChild(tipoConsulta);
        slot.appendChild(estadoLabel);
        
        return slot;
    }

    function crearSlotDisponible(horario) {
        const slot = document.createElement('div');
        slot.className = `appointment-slot available ${horario.tipo.toLowerCase()}`;
        slot.dataset.horarioId = horario.id;
        
        const nombreProfesional = document.createElement('span');
        nombreProfesional.className = 'professional-name';
        nombreProfesional.textContent = horario.medico_nombre;
        
        const tipoConsulta = document.createElement('span');
        tipoConsulta.className = 'appointment-type';
        tipoConsulta.textContent = horario.consultorio || horario.tipo;
        
        const estadoLabel = document.createElement('span');
        estadoLabel.className = 'status-label available';
        estadoLabel.textContent = 'DISPONIBLE';
        
        slot.appendChild(nombreProfesional);
        slot.appendChild(tipoConsulta);
        slot.appendChild(estadoLabel);
        
        return slot;
    }

    function crearSlotVacio() {
        const slot = document.createElement('div');
        slot.className = 'appointment-slot empty';
        
        const label = document.createElement('span');
        label.className = 'slot-label';
        label.textContent = 'Sin horario';
        
        slot.appendChild(label);
        return slot;
    }

    // ========================
    // NAVEGACIÓN DE SEMANAS (MANTENIDA)
    // ========================
    
    semanaAnterior.addEventListener('click', function() {
        fechaActual.setDate(fechaActual.getDate() - 7);
        actualizarPeriodo();
    });

    semanaSiguiente.addEventListener('click', function() {
        fechaActual.setDate(fechaActual.getDate() + 7);
        actualizarPeriodo();
    });

    // ========================
    // GESTIÓN DEL MODAL MEJORADA
    // ========================
    
    nuevoHorarioBtn.addEventListener('click', function() {
        abrirModalCreacion();
    });

    function abrirModalCreacion() {
        modoEdicion = false;
        horarioEditandoId = null;
        
        modalTitle.textContent = 'Crear Horario Disponible';
        btnGuardarTexto.textContent = 'Crear Horario Disponible';
        
        resetearFormulario();
        
        // Establecer fecha mínima como hoy
        const hoy = new Date().toISOString().split('T')[0];
        document.getElementById('horarioFecha').min = hoy;
        document.getElementById('horarioFecha').value = hoy;
        
        modalHorario.style.display = 'block';
    }

    function abrirModalEdicion(datosHorario) {
        modoEdicion = true;
        horarioEditandoId = datosHorario.id;
        
        modalTitle.textContent = 'Editar Horario';
        btnGuardarTexto.textContent = 'Actualizar Horario';
        
        resetearFormulario();
        
        // Prellenar datos
        document.getElementById('horarioProfesional').value = datosHorario.medico_id;
        document.getElementById('horarioFecha').value = datosHorario.fecha;
        
        // Configurar horas
        horarioInicio.value = datosHorario.hora_inicio;
        llenarSelectHoraFin(datosHorario.hora_inicio);
        horarioFin.value = datosHorario.hora_fin;
        
        // Configurar tipo y campos relacionados
        horarioTipo.value = datosHorario.tipo.toLowerCase();
        manejarCambioTipoConsulta(datosHorario.tipo.toLowerCase());
        
        if (datosHorario.consultorio) {
            horarioConsultorio.value = datosHorario.consultorio;
        }
        
        document.getElementById('horarioNotas').value = datosHorario.observaciones || '';
        
        modalHorario.style.display = 'block';
    }

    function resetearFormulario() {
        formHorario.reset();
        
        // Resetear selects específicos
        horarioFin.innerHTML = '<option value="">Se calcula automáticamente</option>';
        
        // Ocultar grupos opcionales
        consultorioGroup.style.display = 'none';
        enlaceZoomGroup.style.display = 'none';
        horarioConsultorio.required = false;
        
        // Limpiar campos
        horarioEnlaceZoom.value = '';
    }

    function cerrarModal() {
        modalHorario.style.display = 'none';
        resetearFormulario();
        modoEdicion = false;
        horarioEditandoId = null;
    }

    closeHorarioModal.addEventListener('click', cerrarModal);
    cancelHorario.addEventListener('click', cerrarModal);

    modalHorario.addEventListener('click', function(e) {
        if (e.target === modalHorario) {
            cerrarModal();
        }
    });

    // ========================
    // VALIDACIÓN Y GUARDADO MEJORADO
    // ========================

    guardarHorario.addEventListener('click', async function() {
        if (validarFormulario()) {
            if (modoEdicion) {
                await actualizarHorarioExistente();
            } else {
                await guardarNuevoHorario();
            }
        }
    });

    function validarFormulario() {
        const profesional = document.getElementById('horarioProfesional').value;
        const fecha = document.getElementById('horarioFecha').value;
        const horaInicio = horarioInicio.value;
        const horaFinVal = horarioFin.value;
        const tipo = horarioTipo.value;
        
        if (!profesional) {
            mostrarError('Debe seleccionar un profesional');
            return false;
        }
        if (!fecha) {
            mostrarError('Debe seleccionar una fecha');
            return false;
        }
        if (!horaInicio) {
            mostrarError('Debe seleccionar hora de inicio');
            return false;
        }
        if (!horaFinVal) {
            mostrarError('Debe seleccionar hora de fin');
            return false;
        }
        if (!tipo) {
            mostrarError('Debe seleccionar el tipo de consulta');
            return false;
        }
        
        // Validaciones específicas por tipo
        if ((tipo === 'presencial' || tipo === 'mixto') && !horarioConsultorio.value) {
            mostrarError('Debe seleccionar un consultorio o sala');
            return false;
        }
        
        return true;
    }

    async function guardarNuevoHorario() {
        try {
            showLoading();
            
            const datos = construirDatosHorario();
            
            const response = await fetch('/admin/horarios/crear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(datos)
            });
            
            const result = await response.json();
            
            if (result.exito) {
                // NUEVO: Mensaje dinámico según número de slots creados
                if (result.slots_creados === 1) {
                    mostrarExito('Slot individual de 1 hora creado exitosamente.');
                } else {
                    mostrarExito(`${result.slots_creados} slots de 1 hora creados exitosamente.`);
                }
                cerrarModal();
                actualizarPeriodo(); // Recargar calendario
            } else {
                mostrarError(result.error);
            }
            
        } catch (error) {
            console.error('Error:', error);
            mostrarError('Error al guardar el horario');
        } finally {
            hideLoading();
        }
    }

    async function actualizarHorarioExistente() {
        try {
            showLoading();
            
            const datos = construirDatosHorario();
            
            const response = await fetch(`/admin/horarios/${horarioEditandoId}/actualizar`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(datos)
            });
            
            const result = await response.json();
            
            if (result.exito) {
                mostrarExito('Horario actualizado exitosamente.');
                cerrarModal();
                actualizarPeriodo(); // Recargar calendario
            } else {
                mostrarError(result.error);
            }
            
        } catch (error) {
            console.error('Error:', error);
            mostrarError('Error al actualizar el horario');
        } finally {
            hideLoading();
        }
    }

    function construirDatosHorario() {
        const tipo = horarioTipo.value.toUpperCase();
        
        const datos = {
            medico_id: parseInt(document.getElementById('horarioProfesional').value),
            fecha: document.getElementById('horarioFecha').value,
            hora_inicio: horarioInicio.value,
            hora_fin: horarioFin.value,
            tipo: tipo,
            observaciones: document.getElementById('horarioNotas').value,
            duracion_cita: 60
        };

        // Agregar consultorio si aplica
        if (tipo === 'PRESENCIAL' || tipo === 'MIXTO') {
            datos.consultorio = horarioConsultorio.value;
        }

        // Agregar enlace zoom si aplica (aunque sea ficticio, se puede guardar en observaciones)
        if (tipo === 'VIRTUAL' || tipo === 'MIXTO') {
            const enlaceZoom = horarioEnlaceZoom.value;
            if (enlaceZoom) {
                // Agregar enlace a las observaciones
                const observacionesActuales = datos.observaciones || '';
                datos.observaciones = observacionesActuales + 
                    (observacionesActuales ? '\n' : '') + 
                    `Enlace de videollamada: ${enlaceZoom}`;
            }
        }

        return datos;
    }

    // =====================
    // INTERACCIÓN CON SLOTS
    // =====================
    
    document.addEventListener('click', async function(e) {
        const slot = e.target.closest('.appointment-slot');
        if (!slot) return;
        
        // Quitar selección anterior
        document.querySelectorAll('.appointment-slot').forEach(s => {
            s.classList.remove('slot-selected');
        });
        
        // Seleccionar slot actual
        slot.classList.add('slot-selected');
        
        // Manejar según tipo de slot
        if (slot.classList.contains('empty')) {
            manejarSlotVacio(slot);
        } else if (slot.classList.contains('available')) {
            manejarSlotDisponible(slot);
        } else if (slot.classList.contains('occupied')) {
            await manejarSlotOcupado(slot);
        }
    });

    function manejarSlotVacio(slot) {
        const fecha = slot.dataset.fecha;
        const hora = slot.dataset.hora;
        
        console.log('Slot vacío seleccionado - crear horario disponible:', fecha, hora);
        
        // Resetear y abrir modal en modo creación
        abrirModalCreacion();
        
        // Prellenar datos del slot seleccionado
        document.getElementById('horarioFecha').value = fecha;
        horarioInicio.value = hora;
        
        // Calcular y establecer hora fin automáticamente
        llenarSelectHoraFin(hora);
    }

    function manejarSlotDisponible(slot) {
        const horarioId = slot.dataset.horarioId;
        
        console.log('Slot disponible seleccionado - el médico está libre:', horarioId);
        
        mostrarInfo(`
            <div style="text-align: center; padding: 20px;">
                <i class="fas fa-calendar-check" style="font-size: 48px; color: #28a745; margin-bottom: 15px;"></i>
                <h4 style="color: #28a745; margin-bottom: 10px;">Horario Disponible</h4>
                <p>Este médico tiene disponibilidad en este horario.</p>
                <p><strong>¿Qué puedes hacer?</strong></p>
                <ul style="text-align: left; display: inline-block;">
                    <li>Agendar una cita para un paciente</li>
                    <li>Ver detalles del horario disponible</li>
                    <li>Modificar el horario si es necesario</li>
                </ul>
                <div style="margin-top: 20px;">
                    <button onclick="editarHorarioSlot('${horarioId}')" 
                            style="background: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin-right: 10px;">
                        <i class="fas fa-edit"></i> Editar Horario
                    </button>
                    <button onclick="eliminarHorarioSlot('${horarioId}')" 
                            style="background: #dc3545; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                        <i class="fas fa-trash"></i> Eliminar
                    </button>
                </div>
            </div>
        `);
    }

    async function manejarSlotOcupado(slot) {
        const horarioId = slot.dataset.horarioId;
        if (!horarioId) return;
        
        console.log('Slot ocupado seleccionado - el médico tiene cita:', horarioId);
        
        try {
            const response = await fetch(`/admin/horarios/${horarioId}`);
            const data = await response.json();
            
            if (data.exito) {
                mostrarDetallesHorario(data.horario);
            }
        } catch (error) {
            console.error('Error al cargar detalles:', error);
        }
    }

    // ========================
    // FUNCIONES GLOBALES PARA BOTONES EN MODALES
    // ========================
    
    window.editarHorarioSlot = async function(horarioId) {
        try {
            // Cerrar modal de información
            document.querySelectorAll('.modal').forEach(modal => {
                if (modal.id !== 'modalHorario') {
                    modal.remove();
                }
            });

            const response = await fetch(`/admin/horarios/${horarioId}`);
            const data = await response.json();
            
            if (data.exito) {
                abrirModalEdicion(data.horario);
            } else {
                mostrarError('Error al cargar datos del horario');
            }
        } catch (error) {
            console.error('Error:', error);
            mostrarError('Error al cargar horario para edición');
        }
    };

    window.eliminarHorarioSlot = async function(horarioId) {
        if (!confirm('¿Está seguro de eliminar este horario? Esta acción no se puede deshacer.')) {
            return;
        }

        try {
            showLoading();
            
            const response = await fetch(`/admin/horarios/${horarioId}/eliminar`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.exito) {
                mostrarExito('Horario eliminado exitosamente');
                
                // Cerrar modal de información
                document.querySelectorAll('.modal').forEach(modal => {
                    if (modal.id !== 'modalHorario') {
                        modal.remove();
                    }
                });
                
                actualizarPeriodo(); // Recargar calendario
            } else {
                mostrarError(result.error);
            }
            
        } catch (error) {
            console.error('Error:', error);
            mostrarError('Error al eliminar horario');
        } finally {
            hideLoading();
        }
    };

    function mostrarDetallesHorario(horario) {
        const tipoInfo = {
            'PRESENCIAL': { icon: 'fas fa-building', color: '#28a745' },
            'VIRTUAL': { icon: 'fas fa-video', color: '#007bff' },
            'MIXTO': { icon: 'fas fa-random', color: '#6610f2' }
        };

        const info = tipoInfo[horario.tipo] || tipoInfo['PRESENCIAL'];

        const mensaje = `
            <div style="text-align: center; margin-bottom: 20px;">
                <i class="${info.icon}" style="font-size: 48px; color: ${info.color}; margin-bottom: 15px;"></i>
                <h4 style="color: #dc3545;">Horario Ocupado</h4>
            </div>
            <div style="text-align: left;">
                <p><strong>Médico:</strong> ${horario.medico_nombre}</p>
                <p><strong>Especialidad:</strong> ${horario.especialidad}</p>
                <p><strong>Fecha:</strong> ${new Date(horario.fecha).toLocaleDateString('es-ES')}</p>
                <p><strong>Horario:</strong> ${horario.hora_inicio} - ${horario.hora_fin}</p>
                <p><strong>Tipo:</strong> <span style="color: ${info.color};">${horario.tipo}</span></p>
                ${horario.consultorio ? `<p><strong>Consultorio:</strong> ${horario.consultorio}</p>` : ''}
                <p><strong>Estado:</strong> <span style="color: #dc3545; font-weight: bold;">OCUPADO</span></p>
                <p><strong>Citas agendadas:</strong> ${horario.total_citas}</p>
                ${horario.observaciones ? `<p><strong>Observaciones:</strong> ${horario.observaciones}</p>` : ''}
            </div>
        `;
        
        mostrarInfo(mensaje);
    }

    // ========================
    // UTILIDADES (MANTENIDAS CON PEQUEÑAS MEJORAS)
    // ========================
    
    function showLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'loading-overlay';
        loadingDiv.innerHTML = `
            <div style="text-align: center;">
                <i class="fas fa-spinner fa-spin" style="font-size: 32px; margin-bottom: 10px;"></i>
                <div>Procesando...</div>
            </div>
        `;
        loadingDiv.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.7); display: flex; justify-content: center;
            align-items: center; z-index: 9999; color: white; font-family: Arial, sans-serif;
        `;
        document.body.appendChild(loadingDiv);
    }

    function hideLoading() {
        const loading = document.getElementById('loading-overlay');
        if (loading) {
            loading.remove();
        }
    }

    function mostrarNotificacion(mensaje, tipo = 'info') {
        const iconos = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'info': 'fas fa-info-circle'
        };

        const notificacion = document.createElement('div');
        notificacion.className = `notification ${tipo} show`;
        notificacion.innerHTML = `
            <i class="${iconos[tipo] || iconos.info}" style="margin-right: 8px;"></i>
            ${mensaje}
        `;
        
        notificacion.style.cssText = `
            position: fixed; top: 20px; right: 20px; 
            padding: 15px 20px; border-radius: 5px; 
            color: white; z-index: 10000; max-width: 400px;
            font-family: Arial, sans-serif; box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            opacity: 0; transform: translateX(100%);
            transition: all 0.3s ease; display: flex; align-items: center;
        `;
        
        // Colores según tipo
        switch(tipo) {
            case 'success':
                notificacion.style.backgroundColor = '#28a745';
                break;
            case 'error':
                notificacion.style.backgroundColor = '#dc3545';
                break;
            default:
                notificacion.style.backgroundColor = '#6c757d';
        }
        
        document.body.appendChild(notificacion);
        
        // Animar entrada
        setTimeout(() => {
            notificacion.style.opacity = '1';
            notificacion.style.transform = 'translateX(0)';
        }, 100);
        
        // Remover después de 4 segundos
        setTimeout(() => {
            if (notificacion.parentNode) {
                notificacion.style.opacity = '0';
                notificacion.style.transform = 'translateX(100%)';
                setTimeout(() => notificacion.remove(), 300);
            }
        }, 4000);
    }

    function mostrarExito(mensaje) {
        mostrarNotificacion(mensaje, 'success');
    }

    function mostrarError(mensaje) {
        mostrarNotificacion(mensaje, 'error');
        console.error('Error:', mensaje);
    }

    function mostrarInfo(mensaje) {
        const modalInfo = document.createElement('div');
        modalInfo.className = 'modal';
        modalInfo.style.display = 'block';
        modalInfo.innerHTML = `
            <div class="modal-overlay" style="background: rgba(0,0,0,0.5);"></div>
            <div class="modal-content" style="
                background: white; 
                border-radius: 8px; 
                max-width: 500px; 
                margin: 50px auto; 
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            ">
                <div class="modal-header" style="
                    padding: 20px 24px 10px; 
                    border-bottom: 1px solid #eee;
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center;
                ">
                    <h3 style="margin: 0; color: #333;">Información del Horario</h3>
                    <button class="modal-close" style="
                        background: none; 
                        border: none; 
                        font-size: 24px; 
                        cursor: pointer; 
                        color: #666;
                    ">&times;</button>
                </div>
                <div class="modal-body" style="padding: 20px 24px;">
                    ${mensaje}
                </div>
                <div class="modal-footer" style="
                    padding: 10px 24px 20px; 
                    text-align: right;
                ">
                    <button class="btn btn-secondary" style="
                        padding: 8px 16px; 
                        background: #6c757d; 
                        color: white; 
                        border: none; 
                        border-radius: 4px; 
                        cursor: pointer;
                    ">Cerrar</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modalInfo);
        
        // Eventos para cerrar
        modalInfo.querySelector('.modal-close').onclick = () => modalInfo.remove();
        modalInfo.querySelector('.btn-secondary').onclick = () => modalInfo.remove();
        modalInfo.onclick = (e) => {
            if (e.target === modalInfo || e.target.className === 'modal-overlay') {
                modalInfo.remove();
            }
        };
    }

    // ========================
    // ATAJOS DE TECLADO (MANTENIDOS)
    // ========================
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (modalHorario.style.display === 'block') {
                cerrarModal();
            }
        }
        
        if (e.key === 'n' && e.ctrlKey) {
            e.preventDefault();
            nuevoHorarioBtn.click();
        }
        
        if (e.key === 'ArrowLeft' && e.ctrlKey) {
            e.preventDefault();
            semanaAnterior.click();
        }
        
        if (e.key === 'ArrowRight' && e.ctrlKey) {
            e.preventDefault();
            semanaSiguiente.click();
        }
    });

    // ========================
    // INICIALIZACIÓN
    // ========================
    
    async function inicializar() {
        try {
            await cargarProfesionalesActivos();
            actualizarPeriodo();
            
            console.log('Sistema de horarios mejorado completamente inicializado');
            console.log('Funcionalidades añadidas:');
            console.log('- Selección de horas por intervalos de 1 hora');
            console.log('- Cálculo automático de hora fin');
            console.log('- Consultorios y salas predefinidos');
            console.log('- Generación automática de enlaces Zoom');
            console.log('- Auto-llenado al hacer clic en slots vacíos');
            console.log('- Modo edición de horarios existentes');
            
        } catch (error) {
            console.error('Error en inicialización:', error);
            mostrarError('Error al inicializar el sistema de horarios');
        }
    }
    
    inicializar();
});