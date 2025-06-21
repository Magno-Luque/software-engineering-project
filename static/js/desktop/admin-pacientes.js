// static/js/desktop/admin-pacientes.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('Página de Pacientes cargada');

    // ========================
    // ELEMENTOS DEL DOM
    // ========================
    const pacientesTable = document.getElementById('pacientesTable');
    
    // Verificar si estamos en la página correcta
    if (!pacientesTable) {
        console.log('No se encontró la tabla de pacientes - Script no continuará');
        return;
    }

    const busquedaInput = document.getElementById('busquedaInput');
    const estadoFilter = document.getElementById('estadoFilter');
    const medicoFilter = document.getElementById('medicoFilter');
    const fechaDesde = document.getElementById('fechaDesde');
    const fechaHasta = document.getElementById('fechaHasta');
    const nuevoPacienteBtn = document.getElementById('nuevoPacienteBtn');
    
    // Modal Cuidador
    const modalCuidador = document.getElementById('modalCuidador');
    const closeCuidadorModal = document.getElementById('closeCuidadorModal');
    const cancelCuidador = document.getElementById('cancelCuidador');
    const guardarCuidador = document.getElementById('guardarCuidador');
    const formCuidador = document.getElementById('formCuidador');

    // ========================
    // MODAL VER PACIENTE
    // ========================
    let modalVerPaciente = null;
    let closeVerPacienteModal = null;
    let cerrarVerPaciente = null;

    // ========================
    // MODAL EDITAR PACIENTE
    // ========================
    let modalEditarPaciente = null;
    let closeEditarPacienteModal = null;
    let cancelarEditar = null;
    let guardarEdicion = null;
    let formEditarPaciente = null;

    // ========================
    // MODAL NUEVO PACIENTE
    // ========================
    let modalNuevoPaciente = null;
    let closeNuevoPacienteModal = null;
    let cancelarNuevoPaciente = null;
    let guardarNuevoPaciente = null;
    let formNuevoPaciente = null;
    let medicosDisponibles = [];

    // ========================
    // INICIALIZACIÓN DE EVENTOS
    // ========================
    function inicializarEventos() {
        // Filtros
        if (busquedaInput) busquedaInput.addEventListener('input', filtrarTabla);
        if (estadoFilter) estadoFilter.addEventListener('change', filtrarTabla);
        if (medicoFilter) medicoFilter.addEventListener('change', filtrarTabla);
        if (fechaDesde) fechaDesde.addEventListener('change', filtrarTabla);
        if (fechaHasta) fechaHasta.addEventListener('change', filtrarTabla);

        // Botón nuevo paciente
        if (nuevoPacienteBtn) {
            nuevoPacienteBtn.addEventListener('click', function() {
                if (!modalNuevoPaciente) {
                    crearModalNuevoPaciente();
                }
                modalNuevoPaciente.style.display = 'block';
            });
        }

        // Modal cuidador
        if (modalCuidador && closeCuidadorModal && cancelCuidador) {
            closeCuidadorModal.addEventListener('click', cerrarModalCuidador);
            cancelCuidador.addEventListener('click', cerrarModalCuidador);
            modalCuidador.addEventListener('click', function(e) {
                if (e.target === modalCuidador) {
                    cerrarModalCuidador();
                }
            });
        }

        if (guardarCuidador && formCuidador) {
            guardarCuidador.addEventListener('click', guardarCuidadorHandler);
        }

        // Delegación de eventos para la tabla
        pacientesTable.addEventListener('click', function(e) {
            const target = e.target.closest('.btn-action');
            if (!target) return;
            
            const row = target.closest('tr');
            const pacienteId = row.cells[0].textContent;
            const pacienteNombre = row.cells[1].textContent;
            
            if (target.classList.contains('btn-view')) {
                verPaciente(pacienteId, pacienteNombre);
            } else if (target.classList.contains('btn-edit')) {
                editarPaciente(pacienteId, pacienteNombre);
            } else if (target.classList.contains('btn-toggle')) {
                toggleEstadoPaciente(target, row, pacienteId);
            }
        });

        // Inicializar estados de los toggles
        setTimeout(inicializarEstadosToggle, 500);
        
        // Establecer fecha máxima como hoy
        const hoy = new Date().toISOString().split('T')[0];
        if (fechaDesde) fechaDesde.max = hoy;
        if (fechaHasta) fechaHasta.max = hoy;
        
        // Contador inicial
        actualizarContadorResultados();
    }

    // Llamar a la inicialización
    inicializarEventos();

    // ========================
    // FUNCIONALIDAD DE FILTROS
    // ========================
    function filtrarTabla() {
        const rows = pacientesTable.querySelectorAll('tbody tr');
        const termino = busquedaInput ? busquedaInput.value.toLowerCase() : '';
        const estado = estadoFilter ? estadoFilter.value : 'todos';
        const medico = medicoFilter ? medicoFilter.value : 'todos';
        
        rows.forEach(row => {
            const nombre = row.cells[1].textContent.toLowerCase();
            const dni = row.cells[2].textContent.toLowerCase();
            const estadoPaciente = row.cells[7].textContent.toLowerCase();
            const medicoPaciente = row.cells[5].textContent.toLowerCase();
            
            let mostrar = true;
            
            // Filtro de búsqueda (nombre o DNI)
            if (termino && !nombre.includes(termino) && !dni.includes(termino)) {
                mostrar = false;
            }
            
            // Filtro de estado
            if (estado !== 'todos') {
                if (estado === 'activo' && !estadoPaciente.includes('activo')) {
                    mostrar = false;
                }
                if (estado === 'inactivo' && !estadoPaciente.includes('inactivo')) {
                    mostrar = false;
                }
            }
            
            // Filtro de médico (simplificado)
            if (medico !== 'todos') {
                console.log('Filtrar por médico:', medico);
            }
            
            row.style.display = mostrar ? '' : 'none';
        });
        
        actualizarContadorResultados();
    }

    function actualizarContadorResultados() {
        const rows = pacientesTable.querySelectorAll('tbody tr');
        const visibles = Array.from(rows).filter(row => row.style.display !== 'none').length;
        const total = rows.length;
        
        const paginationInfo = document.querySelector('.pagination-info');
        if (paginationInfo) {
            paginationInfo.textContent = `Mostrando ${visibles} de ${total} pacientes`;
        }
    }

    // ========================
    // FUNCIONES PARA PACIENTES
    // ========================
    function verPaciente(id, nombre) {
        console.log(`Ver detalles del paciente: ${nombre} (ID: ${id})`);
        
        if (!id || !nombre) {
            console.error('Error: ID o nombre del paciente no definidos', {id, nombre});
            alert('Error: No se pudo obtener la información del paciente');
            return;
        }
        
        if (!modalVerPaciente) {
            crearModalVerPaciente();
        }
        
        mostrarLoadingModal();
        modalVerPaciente.style.display = 'block';
        
        fetch(`/admin/pacientes/api/${id}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    mostrarDetallesPaciente(data.paciente);
                } else {
                    mostrarErrorModal(data.message || 'Error al cargar los datos del paciente');
                }
            })
            .catch(error => {
                console.error('Error completo:', error);
                mostrarErrorModal('Error de conexión al servidor: ' + error.message);
            });
    }

    function editarPaciente(id, nombre) {
        console.log(`Editar paciente: ${nombre} (ID: ${id})`);
        
        if (!id || !nombre) {
            console.error('Error: ID o nombre del paciente no definidos', {id, nombre});
            alert('Error: No se pudo obtener la información del paciente');
            return;
        }
        
        if (!modalEditarPaciente) {
            crearModalEditarPaciente();
        }
        
        mostrarLoadingEdicion();
        modalEditarPaciente.style.display = 'block';
        
        fetch(`/admin/pacientes/api/${id}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    cargarFormularioEdicion(data.paciente);
                } else {
                    mostrarErrorEdicion(data.message || 'Error al cargar los datos del paciente');
                }
            })
            .catch(error => {
                console.error('Error al cargar datos para edición:', error);
                mostrarErrorEdicion('Error de conexión al servidor: ' + error.message);
            });
    }

    function toggleEstadoPaciente(button, row, id) {
        console.log('=== DEBUG TOGGLE ESTADO ===');
        
        let statusSpan = row.querySelector('.status') || row.querySelector('.estado');
        
        if (!statusSpan) {
            for (let i = 0; i < row.cells.length; i++) {
                const cellText = row.cells[i].textContent.trim().toUpperCase();
                if (cellText === 'ACTIVO' || cellText === 'INACTIVO') {
                    statusSpan = row.cells[i].querySelector('span') || row.cells[i];
                    break;
                }
            }
        }
        
        if (!statusSpan) {
            console.error('❌ No se pudo encontrar el elemento de estado');
            alert('Error: No se pudo encontrar el elemento de estado en la fila');
            return;
        }
        
        const isActive = statusSpan.classList.contains('active') || 
                        statusSpan.textContent.trim().toUpperCase() === 'ACTIVO';
        
        const url = `/admin/pacientes/api/${id}/toggle-estado`;
        
        button.disabled = true;
        button.style.opacity = '0.6';
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                cambiarEstadoVisual(statusSpan, button, row, data.nuevo_estado);
                alert(`✅ ${data.message}`);
            } else {
                alert('❌ Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('❌ Error completo:', error);
            alert('❌ Error de conexión: ' + error.message);
        })
        .finally(() => {
            button.disabled = false;
            button.style.opacity = '1';
        });
    }

    function cambiarEstadoVisual(statusSpan, button, row, nuevoEstado) {
        const esActivo = nuevoEstado === 'ACTIVO';
        
        if (!statusSpan.classList.contains('status') && !statusSpan.classList.contains('estado')) {
            statusSpan.classList.add('status');
        }
        
        if (esActivo) {
            statusSpan.classList.remove('inactive');
            statusSpan.classList.add('active');
            statusSpan.textContent = 'ACTIVO';
            
            button.classList.remove('inactive');
            button.classList.add('active');
            
            const icon = button.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-toggle-on';
            }
        } else {
            statusSpan.classList.remove('active');
            statusSpan.classList.add('inactive');
            statusSpan.textContent = 'INACTIVO';
            
            button.classList.remove('active');
            button.classList.add('inactive');
            
            const icon = button.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-toggle-off';
            }
        }
    }

    function inicializarEstadosToggle() {
        const filas = pacientesTable.querySelectorAll('tbody tr');
        
        filas.forEach(fila => {
            let statusElement = fila.querySelector('.status') || fila.querySelector('.estado');
            
            if (!statusElement) {
                for (let i = 0; i < fila.cells.length; i++) {
                    const cellText = fila.cells[i].textContent.trim().toUpperCase();
                    if (cellText === 'ACTIVO' || cellText === 'INACTIVO') {
                        statusElement = fila.cells[i].querySelector('span') || fila.cells[i];
                        break;
                    }
                }
            }
            
            if (!statusElement) return;
            
            const toggleButton = fila.querySelector('.btn-toggle');
            if (!toggleButton) return;
            
            const estadoTexto = statusElement.textContent.trim().toUpperCase();
            const esActivo = estadoTexto === 'ACTIVO';
            
            if (!statusElement.classList.contains('status')) {
                statusElement.classList.add('status');
            }
            
            if (esActivo) {
                statusElement.classList.remove('inactive');
                statusElement.classList.add('active');
            } else {
                statusElement.classList.remove('active');
                statusElement.classList.add('inactive');
            }
            
            const iconElement = toggleButton.querySelector('i');
            
            if (esActivo) {
                toggleButton.classList.remove('inactive');
                toggleButton.classList.add('active');
                if (iconElement) {
                    iconElement.className = 'fas fa-toggle-on';
                }
            } else {
                toggleButton.classList.remove('active');
                toggleButton.classList.add('inactive');
                if (iconElement) {
                    iconElement.className = 'fas fa-toggle-off';
                }
            }
        });
    }

    // ========================
    // MODALES
    // ========================
    function crearModalVerPaciente() {
        const modalHTML = `
            <div id="modalVerPaciente" class="modal-container" style="display: none;">
                <div class="modal">
                    <div class="modal-header">
                        <h3>Detalles del Paciente</h3>
                        <button type="button" class="close-btn" id="closeVerPacienteModal">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <div id="pacienteDetallesContent"></div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" id="cerrarVerPaciente">
                            <i class="fas fa-times"></i> Cerrar
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        modalVerPaciente = document.getElementById('modalVerPaciente');
        closeVerPacienteModal = document.getElementById('closeVerPacienteModal');
        cerrarVerPaciente = document.getElementById('cerrarVerPaciente');
        
        closeVerPacienteModal.addEventListener('click', cerrarModalVerPaciente);
        cerrarVerPaciente.addEventListener('click', cerrarModalVerPaciente);
        
        modalVerPaciente.addEventListener('click', function(e) {
            if (e.target === modalVerPaciente) {
                cerrarModalVerPaciente();
            }
        });
    }

    function mostrarLoadingModal() {
        const modalContent = document.getElementById('pacienteDetallesContent');
        if (modalContent) {
            modalContent.innerHTML = `
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <p>Cargando información del paciente...</p>
                </div>
            `;
        }
    }

    function mostrarErrorModal(mensaje) {
        const modalContent = document.getElementById('pacienteDetallesContent');
        if (modalContent) {
            modalContent.innerHTML = `
                <div class="error-container">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p class="error-message">${mensaje}</p>
                </div>
            `;
        }
    }

    function mostrarDetallesPaciente(paciente) {
        const modalContent = document.getElementById('pacienteDetallesContent');
        
        const enfermedadesHTML = paciente.enfermedades && paciente.enfermedades.length > 0 
            ? paciente.enfermedades.map(enfermedad => 
                `<span class="enfermedad-tag ${enfermedad.toLowerCase()}">${enfermedad}</span>`
            ).join('')
            : '<span class="no-data">Sin enfermedades registradas</span>';
        
        const cuidadoresHTML = paciente.cuidadores && paciente.cuidadores.length > 0 
            ? paciente.cuidadores.map(cuidador => `
                <div class="cuidador-item">
                    <div class="cuidador-info">
                        <h4>${cuidador.nombre_completo}</h4>
                        <p><strong>DNI:</strong> ${cuidador.dni}</p>
                        <p><strong>Teléfono:</strong> ${cuidador.telefono}</p>
                        <p><strong>Relación:</strong> ${cuidador.relacion}</p>
                        <span class="status ${cuidador.estado.toLowerCase()}">${cuidador.estado.toUpperCase()}</span>
                    </div>
                </div>
            `).join('')
            : '<p class="no-data">No tiene cuidadores asignados</p>';
        
        modalContent.innerHTML = `
            <div class="paciente-detalle">
                <!-- Información Personal -->
                <div class="detalle-seccion">
                    <h3><i class="fas fa-user"></i> Información Personal</h3>
                    <div class="detalle-grid">
                        <div class="detalle-item">
                            <label>Nombre completo:</label>
                            <span>${paciente.nombre_completo}</span>
                        </div>
                        <div class="detalle-item">
                            <label>DNI:</label>
                            <span>${paciente.dni}</span>
                        </div>
                        <div class="detalle-item">
                            <label>Fecha de nacimiento:</label>
                            <span>${paciente.fecha_nacimiento}</span>
                        </div>
                        <div class="detalle-item">
                            <label>Edad:</label>
                            <span>${paciente.edad} años</span>
                        </div>
                        <div class="detalle-item">
                            <label>Email:</label>
                            <span>${paciente.email || 'No registrado'}</span>
                        </div>
                        <div class="detalle-item">
                            <label>Teléfono:</label>
                            <span>${paciente.telefono || 'No registrado'}</span>
                        </div>
                        <div class="detalle-item full-width">
                            <label>Dirección:</label>
                            <span>${paciente.direccion || 'No registrada'}</span>
                        </div>
                        <div class="detalle-item">
                            <label>Estado:</label>
                            <span class="status ${paciente.estado.toLowerCase()}">${paciente.estado.toUpperCase()}</span>
                        </div>
                        <div class="detalle-item">
                            <label>Fecha de registro:</label>
                            <span>${paciente.fecha_registro}</span>
                        </div>
                    </div>
                </div>

                <!-- Información Médica -->
                <div class="detalle-seccion">
                    <h3><i class="fas fa-heartbeat"></i> Información Médica</h3>
                    <div class="detalle-grid">
                        <div class="detalle-item">
                            <label>Médico asignado:</label>
                            <span>${paciente.medico_asignado ? 
                                `${paciente.medico_asignado.nombre} - ${paciente.medico_asignado.especialidad}` : 
                                'No asignado'}</span>
                        </div>
                        <div class="detalle-item full-width">
                            <label>Enfermedades:</label>
                            <div class="enfermedades-container">
                                ${enfermedadesHTML}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Cuidadores -->
                <div class="detalle-seccion">
                    <h3><i class="fas fa-user-friends"></i> Cuidadores</h3>
                    <div class="cuidadores-lista">
                        ${cuidadoresHTML}
                    </div>
                </div>
            </div>
        `;
    }

    function cerrarModalVerPaciente() {
        if (modalVerPaciente) {
            modalVerPaciente.style.display = 'none';
        }
    }

    // ========================
    // MODAL EDITAR PACIENTE
    // ========================
    function crearModalEditarPaciente() {
        const modalHTML = `
            <div id="modalEditarPaciente" class="modal-container" style="display: none;">
                <div class="modal modal-editar">
                    <div class="modal-header">
                        <h3>Editar Paciente</h3>
                        <button type="button" class="close-btn" id="closeEditarPacienteModal">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <div id="pacienteEdicionContent"></div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" id="cancelarEditar">
                            <i class="fas fa-times"></i> Cancelar
                        </button>
                        <button type="button" class="btn btn-primary" id="guardarEdicion">
                            <i class="fas fa-save"></i> Guardar Cambios
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        modalEditarPaciente = document.getElementById('modalEditarPaciente');
        closeEditarPacienteModal = document.getElementById('closeEditarPacienteModal');
        cancelarEditar = document.getElementById('cancelarEditar');
        guardarEdicion = document.getElementById('guardarEdicion');
        
        closeEditarPacienteModal.addEventListener('click', cerrarModalEditarPaciente);
        cancelarEditar.addEventListener('click', cerrarModalEditarPaciente);
        
        modalEditarPaciente.addEventListener('click', function(e) {
            if (e.target === modalEditarPaciente) {
                cerrarModalEditarPaciente();
            }
        });
        
        guardarEdicion.addEventListener('click', procesarEdicionPaciente);
    }

    function mostrarLoadingEdicion() {
        const modalContent = document.getElementById('pacienteEdicionContent');
        if (modalContent) {
            modalContent.innerHTML = `
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <p>Cargando datos del paciente...</p>
                </div>
            `;
        }
    }

    function mostrarErrorEdicion(mensaje) {
        const modalContent = document.getElementById('pacienteEdicionContent');
        if (modalContent) {
            modalContent.innerHTML = `
                <div class="error-container">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p class="error-message">${mensaje}</p>
                </div>
            `;
        }
    }

    function cargarFormularioEdicion(paciente) {
        const modalContent = document.getElementById('pacienteEdicionContent');
        
        const enfermedades = ['diabetes', 'hipertension', 'asma', 'cardiovascular'];
        const enfermedadesCheckboxes = enfermedades.map(enfermedad => {
            const checked = paciente.enfermedades.includes(enfermedad) ? 'checked' : '';
            return `
                <label class="checkbox-enfermedad">
                    <input type="checkbox" name="enfermedades" value="${enfermedad}" ${checked} data-especialidad="${obtenerEspecialidadPorEnfermedad(enfermedad)}">
                    <span class="checkmark"></span>
                    ${enfermedad.charAt(0).toUpperCase() + enfermedad.slice(1)}
                </label>
            `;
        }).join('');
        
        const cuidadorHTML = paciente.cuidadores && paciente.cuidadores.length > 0 
            ? `
                <div class="cuidador-actual">
                    <h5>Cuidador Actual</h5>
                    <div class="form-grid">
                        <div class="form-group">
                            <label for="cuidador_nombre">Nombre completo *</label>
                            <input type="text" id="cuidador_nombre" name="cuidador_nombre" 
                                value="${paciente.cuidadores[0].nombre_completo}" required>
                        </div>
                        <div class="form-group">
                            <label for="cuidador_dni">DNI *</label>
                            <input type="text" id="cuidador_dni" name="cuidador_dni" 
                                value="${paciente.cuidadores[0].dni}" required maxlength="8">
                        </div>
                        <div class="form-group">
                            <label for="cuidador_telefono">Teléfono *</label>
                            <input type="tel" id="cuidador_telefono" name="cuidador_telefono" 
                                value="${paciente.cuidadores[0].telefono}" required>
                        </div>
                        <div class="form-group">
                            <label for="cuidador_relacion">Relación *</label>
                            <select id="cuidador_relacion" name="cuidador_relacion" required>
                                <option value="">Seleccionar...</option>
                                <option value="hijo" ${paciente.cuidadores[0].relacion === 'hijo' ? 'selected' : ''}>Hijo/a</option>
                                <option value="padre" ${paciente.cuidadores[0].relacion === 'padre' ? 'selected' : ''}>Padre/Madre</option>
                                <option value="hermano" ${paciente.cuidadores[0].relacion === 'hermano' ? 'selected' : ''}>Hermano/a</option>
                                <option value="conyugue" ${paciente.cuidadores[0].relacion === 'conyugue' ? 'selected' : ''}>Cónyuge</option>
                                <option value="familiar" ${paciente.cuidadores[0].relacion === 'familiar' ? 'selected' : ''}>Otro familiar</option>
                                <option value="amigo" ${paciente.cuidadores[0].relacion === 'amigo' ? 'selected' : ''}>Amistad</option>
                                <option value="profesional" ${paciente.cuidadores[0].relacion === 'profesional' ? 'selected' : ''}>Cuidador profesional</option>
                                <option value="otro" ${paciente.cuidadores[0].relacion === 'otro' ? 'selected' : ''}>Otro</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <button type="button" class="btn-eliminar-cuidador">
                                <i class="fas fa-trash"></i> Eliminar cuidador
                            </button>
                        </div>
                    </div>
                    <input type="hidden" name="cuidador_id" value="${paciente.cuidadores[0].id}">
                </div>
            `
            : `
                <div class="sin-cuidador">
                    <p>Este paciente no tiene cuidador registrado.</p>
                    <button type="button" id="agregarCuidador" class="btn btn-outline">
                        <i class="fas fa-plus"></i> Agregar cuidador
                    </button>
                </div>
            `;
        
        modalContent.innerHTML = `
            <form id="formEditarPaciente" class="form-editar-paciente">
                <!-- Información Personal -->
                <div class="form-section">
                    <h4><i class="fas fa-user"></i> Información Personal</h4>
                    <div class="form-grid">
                        <div class="form-group">
                            <label for="editNombres">Nombres *</label>
                            <input type="text" id="editNombres" name="nombres" value="${paciente.nombres || ''}" required>
                        </div>
                        <div class="form-group">
                            <label for="editApellidos">Apellidos *</label>
                            <input type="text" id="editApellidos" name="apellidos" value="${paciente.apellidos || ''}" required>
                        </div>
                        <div class="form-group">
                            <label for="editDni">DNI *</label>
                            <input type="text" id="editDni" name="dni" value="${paciente.dni}" required maxlength="8" pattern="[0-9]{8}">
                        </div>
                        <div class="form-group">
                            <label for="editFechaNacimiento">Fecha de Nacimiento *</label>
                            <input type="date" id="editFechaNacimiento" name="fecha_nacimiento" value="${paciente.fecha_nacimiento}" required>
                        </div>
                        <div class="form-group">
                            <label for="editEmail">Email</label>
                            <input type="email" id="editEmail" name="email" value="${paciente.email || ''}">
                        </div>
                        <div class="form-group">
                            <label for="editTelefono">Teléfono</label>
                            <input type="tel" id="editTelefono" name="telefono" value="${paciente.telefono || ''}" placeholder="Ej: 987654321">
                        </div>
                        <div class="form-group full-width">
                            <label for="editDireccion">Dirección</label>
                            <textarea id="editDireccion" name="direccion" rows="2">${paciente.direccion || ''}</textarea>
                        </div>
                    </div>
                </div>

                <!-- Información Médica -->
                <div class="form-section">
                    <h4><i class="fas fa-heartbeat"></i> Información Médica</h4>
                    
                    <!-- Enfermedades -->
                    <div class="form-group">
                        <label>Enfermedades</label>
                        <div class="enfermedades-checkboxes">
                            ${enfermedadesCheckboxes}
                        </div>
                    </div>
                    
                    <!-- Médicos asignados -->
                    <div class="form-group">
                        <label><strong>Asignación de Médicos:</strong></label>
                        <div id="contenedorMedicosPorEnfermedad" class="medicos-por-enfermedad">
                            <!-- Se cargará dinámicamente -->
                        </div>
                    </div>
                </div>

                <!-- Cuidador -->
                <div class="form-section">
                    <h4><i class="fas fa-user-friends"></i> Cuidador</h4>
                    <div id="cuidador-container">
                        ${cuidadorHTML}
                    </div>
                </div>

                <!-- Campo oculto para el ID -->
                <input type="hidden" name="paciente_id" value="${paciente.id}">
            </form>
        `;
        
        configurarValidacionesBasicas();
        configurarEventosCuidador();
        cargarMedicosParaEdicion(paciente);
    }

    function procesarEdicionPaciente() {
        const form = document.getElementById('formEditarPaciente');
        if (!form) {
            alert('Error: No se encontró el formulario');
            return;
        }
        
        if (!validarFormularioEdicion(form)) {
            return;
        }
        
        const formData = new FormData(form);
        
        const enfermedadesSeleccionadas = [];
        const checkboxes = form.querySelectorAll('input[name="enfermedades"]:checked');
        checkboxes.forEach(checkbox => {
            enfermedadesSeleccionadas.push(checkbox.value);
        });
        
        const medicosAsignados = {};
        const selectoresMedicos = form.querySelectorAll('select[name^="medico_"]');
        selectoresMedicos.forEach(select => {
            if (select.value) {
                const enfermedad = select.name.replace('medico_', '');
                medicosAsignados[enfermedad] = select.value;
            }
        });
        
        const datosActualizados = {
            paciente_id: formData.get('paciente_id'),
            nombres: formData.get('nombres').trim(),
            apellidos: formData.get('apellidos').trim(),
            dni: formData.get('dni').trim(),
            fecha_nacimiento: formData.get('fecha_nacimiento'),
            email: formData.get('email').trim(),
            telefono: formData.get('telefono').trim(),
            direccion: formData.get('direccion').trim(),
            enfermedades: enfermedadesSeleccionadas,
            medicos_asignados: medicosAsignados
        };
        
        const cuidadorNombre = formData.get('cuidador_nombre');
        const cuidadorId = formData.get('cuidador_id');
        const eliminarCuidador = formData.get('eliminar_cuidador');
        
        if (eliminarCuidador === 'true') {
            datosActualizados.eliminar_cuidador = 'true';
        } else if (cuidadorNombre && cuidadorNombre.trim()) {
            datosActualizados.cuidador_id = cuidadorId;
            datosActualizados.cuidador_nombre = cuidadorNombre;
            datosActualizados.cuidador_dni = formData.get('cuidador_dni');
            datosActualizados.cuidador_telefono = formData.get('cuidador_telefono');
            datosActualizados.cuidador_relacion = formData.get('cuidador_relacion');
        }
        
        guardarEdicion.disabled = true;
        guardarEdicion.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
        
        fetch(`/admin/pacientes/api/${datosActualizados.paciente_id}/actualizar`, {
            method: 'PUT',  
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(datosActualizados)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Paciente actualizado exitosamente');
                cerrarModalEditarPaciente();
                location.reload();
            } else {
                alert('Error al actualizar: ' + (data.message || 'Error desconocido'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error de conexión al servidor');
        })
        .finally(() => {
            guardarEdicion.disabled = false;
            guardarEdicion.innerHTML = '<i class="fas fa-save"></i> Guardar Cambios';
        });
    }

    function cerrarModalEditarPaciente() {
        if (modalEditarPaciente) {
            modalEditarPaciente.style.display = 'none';
            const content = document.getElementById('pacienteEdicionContent');
            if (content) {
                content.innerHTML = '';
            }
        }
    }

    // ========================
    // MODAL NUEVO PACIENTE
    // ========================
    function crearModalNuevoPaciente() {
        const modalHTML = `
            <div id="modalNuevoPaciente" class="modal-container" style="display: none;">
                <div class="modal modal-nuevo-paciente">
                    <div class="modal-header">
                        <h3><i class="fas fa-user-plus"></i> Crear Nuevo Paciente</h3>
                        <button type="button" class="close-btn" id="closeNuevoPacienteModal">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <form id="formNuevoPaciente" class="form-nuevo-paciente">
                            <!-- Información Personal -->
                            <div class="form-section">
                                <h4><i class="fas fa-user"></i> Información Personal</h4>
                                <div class="form-grid">
                                    <div class="form-group">
                                        <label for="nuevoNombres">Nombres *</label>
                                        <input type="text" id="nuevoNombres" name="nombres" required maxlength="100">
                                    </div>
                                    <div class="form-group">
                                        <label for="nuevoApellidos">Apellidos *</label>
                                        <input type="text" id="nuevoApellidos" name="apellidos" required maxlength="100">
                                    </div>
                                    <div class="form-group">
                                        <label for="nuevoDni">DNI *</label>
                                        <input type="text" id="nuevoDni" name="dni" required maxlength="8" pattern="[0-9]{8}" placeholder="12345678">
                                    </div>
                                    <div class="form-group">
                                        <label for="nuevoFechaNacimiento">Fecha de Nacimiento *</label>
                                        <input type="date" id="nuevoFechaNacimiento" name="fecha_nacimiento" required>
                                    </div>
                                    <div class="form-group">
                                        <label for="nuevoEmail">Email *</label>
                                        <input type="email" id="nuevoEmail" name="email" required placeholder="ejemplo@correo.com">
                                    </div>
                                    <div class="form-group">
                                        <label for="nuevoTelefono">Teléfono</label>
                                        <input type="tel" id="nuevoTelefono" name="telefono" placeholder="987654321" maxlength="9">
                                    </div>
                                    <div class="form-group full-width">
                                        <label for="nuevoDireccion">Dirección</label>
                                        <textarea id="nuevoDireccion" name="direccion" rows="2" placeholder="Ingrese la dirección completa"></textarea>
                                    </div>
                                </div>
                            </div>

                            <!-- Información Médica -->
                            <div class="form-section">
                                <h4><i class="fas fa-heartbeat"></i> Información Médica</h4>
                                
                                <!-- Enfermedades -->
                                <div class="form-group">
                                    <label>Enfermedades</label>
                                    <div class="enfermedades-checkboxes">
                                        <label class="checkbox-enfermedad">
                                            <input type="checkbox" name="enfermedades" value="diabetes" data-especialidad="ENDOCRINOLOGÍA">
                                            <span class="checkmark"></span>
                                            Diabetes
                                        </label>
                                        <label class="checkbox-enfermedad">
                                            <input type="checkbox" name="enfermedades" value="hipertension" data-especialidad="MEDICINA INTERNA">
                                            <span class="checkmark"></span>
                                            Hipertensión
                                        </label>
                                        <label class="checkbox-enfermedad">
                                            <input type="checkbox" name="enfermedades" value="asma" data-especialidad="NEUMOLOGÍA">
                                            <span class="checkmark"></span>
                                            Asma
                                        </label>
                                        <label class="checkbox-enfermedad">
                                            <input type="checkbox" name="enfermedades" value="cardiovascular" data-especialidad="CARDIOLOGÍA">
                                            <span class="checkmark"></span>
                                            Cardiovascular
                                        </label>
                                    </div>
                                </div>
                                
                                <!-- Médicos asignados -->
                                <div class="form-group">
                                    <label><strong>Asignación de Médicos:</strong></label>
                                    <div id="contenedorMedicosPorEnfermedad" class="medicos-por-enfermedad">
                                        <p class="text-muted">Primero seleccione las enfermedades...</p>
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" id="cancelarNuevoPaciente">
                            <i class="fas fa-times"></i> Cancelar
                        </button>
                        <button type="button" class="btn btn-primary" id="guardarNuevoPaciente">
                            <i class="fas fa-save"></i> Crear Paciente
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        modalNuevoPaciente = document.getElementById('modalNuevoPaciente');
        closeNuevoPacienteModal = document.getElementById('closeNuevoPacienteModal');
        cancelarNuevoPaciente = document.getElementById('cancelarNuevoPaciente');
        guardarNuevoPaciente = document.getElementById('guardarNuevoPaciente');
        formNuevoPaciente = document.getElementById('formNuevoPaciente');
        
        closeNuevoPacienteModal.addEventListener('click', cerrarModalNuevoPaciente);
        cancelarNuevoPaciente.addEventListener('click', cerrarModalNuevoPaciente);
        
        modalNuevoPaciente.addEventListener('click', function(e) {
            if (e.target === modalNuevoPaciente) {
                cerrarModalNuevoPaciente();
            }
        });
        
        guardarNuevoPaciente.addEventListener('click', procesarCreacionPaciente);
        
        const checkboxesEnfermedades = formNuevoPaciente.querySelectorAll('input[name="enfermedades"]');
        checkboxesEnfermedades.forEach(checkbox => {
            checkbox.addEventListener('change', actualizarMedicosPorEnfermedades);
        });
        
        configurarValidacionesNuevoPaciente();
        cargarMedicosDisponibles();
    }

    function actualizarMedicosPorEnfermedades() {
        const checkboxesSeleccionados = formNuevoPaciente.querySelectorAll('input[name="enfermedades"]:checked');
        const todosLosCheckboxes = formNuevoPaciente.querySelectorAll('input[name="enfermedades"]');
        const contenedorMedicos = document.getElementById('contenedorMedicosPorEnfermedad');
        
        contenedorMedicos.innerHTML = '';
        
        if (checkboxesSeleccionados.length === 0) {
            contenedorMedicos.innerHTML = '<p class="text-muted">Primero seleccione las enfermedades...</p>';
            return;
        }
        
        const todasSeleccionadas = checkboxesSeleccionados.length === todosLosCheckboxes.length;
        
        if (todasSeleccionadas) {
            const medicosMedicinaInterna = medicosDisponibles.filter(medico => {
                if (medico.especialidades && Array.isArray(medico.especialidades)) {
                    return medico.especialidades.includes('MEDICINA INTERNA');
                }
                return medico.especialidad === 'MEDICINA INTERNA';
            });
            
            const selectHTML = `
                <div class="form-group medico-enfermedad">
                    <label><strong>Médico para todas las enfermedades (Medicina Interna):</strong></label>
                    <select name="medico_medicina_interna" class="form-control">
                        <option value="">Seleccionar médico especialista en Medicina Interna...</option>
                        ${medicosMedicinaInterna.map(medico => 
                            `<option value="${medico.id}">Dr. ${medico.nombre_formal} - MEDICINA INTERNA</option>`
                        ).join('')}
                    </select>
                </div>
            `;
            
            contenedorMedicos.innerHTML = selectHTML;
        } else {
            checkboxesSeleccionados.forEach(checkbox => {
                const enfermedad = checkbox.value;
                const especialidadRequerida = checkbox.getAttribute('data-especialidad');
                
                const medicosParaEspecialidad = medicosDisponibles.filter(medico => {
                    if (medico.especialidades && Array.isArray(medico.especialidades)) {
                        return medico.especialidades.includes(especialidadRequerida);
                    }
                    return medico.especialidad === especialidadRequerida;
                });
                
                const selectHTML = `
                    <div class="form-group medico-enfermedad">
                        <label><strong>Médico para ${enfermedad}:</strong></label>
                        <select name="medico_${enfermedad}" class="form-control" data-enfermedad="${enfermedad}">
                            <option value="">Seleccionar médico para ${enfermedad}...</option>
                            ${medicosParaEspecialidad.map(medico => 
                                `<option value="${medico.id}">Dr. ${medico.nombre_formal} - ${especialidadRequerida}</option>`
                            ).join('')}
                        </select>
                        ${medicosParaEspecialidad.length === 0 ? 
                            `<small class="text-danger">No hay médicos disponibles para ${enfermedad}</small>` : 
                            `<small class="text-muted">Especialidad: ${especialidadRequerida}</small>`
                        }
                    </div>
                `;
                
                contenedorMedicos.insertAdjacentHTML('beforeend', selectHTML);
            });
        }
    }

    function configurarValidacionesNuevoPaciente() {
        const dniInput = document.getElementById('nuevoDni');
        dniInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '').substring(0, 8);
        });
        
        const nombresInput = document.getElementById('nuevoNombres');
        const apellidosInput = document.getElementById('nuevoApellidos');
        
        [nombresInput, apellidosInput].forEach(input => {
            input.addEventListener('input', function() {
                this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '');
            });
        });
        
        const telefonoInput = document.getElementById('nuevoTelefono');
        telefonoInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '').substring(0, 9);
        });
        
        const fechaInput = document.getElementById('nuevoFechaNacimiento');
        const hoy = new Date().toISOString().split('T')[0];
        fechaInput.max = hoy;
    }

    function cargarMedicosDisponibles() {
        fetch('/admin/pacientes/api/medicos')
            .then(response => response.json())
            .then(data => {
                if (data.medicos) {
                    medicosDisponibles = data.medicos;
                    actualizarMedicosPorEnfermedades();
                }
            })
            .catch(error => {
                console.error('Error al cargar médicos:', error);
            });
    }

    function cerrarModalNuevoPaciente() {
        if (modalNuevoPaciente) {
            modalNuevoPaciente.style.display = 'none';
            if (formNuevoPaciente) {
                formNuevoPaciente.reset();
                actualizarMedicosPorEnfermedades();
            }
        }
    }

    function procesarCreacionPaciente() {
        if (!validarFormularioNuevoPaciente()) {
            return;
        }
        
        const formData = new FormData(formNuevoPaciente);
        
        const enfermedadesSeleccionadas = [];
        const checkboxes = formNuevoPaciente.querySelectorAll('input[name="enfermedades"]:checked');
        checkboxes.forEach(checkbox => {
            enfermedadesSeleccionadas.push(checkbox.value);
        });
        
        const medicosAsignados = {};
        const selectoresMedicos = document.querySelectorAll('select[name^="medico_"]');
        selectoresMedicos.forEach(select => {
            if (select.value) {
                const nombreSelect = select.name;
                if (nombreSelect === 'medico_medicina_interna') {
                    medicosAsignados['medicina_interna'] = select.value;
                } else {
                    const enfermedad = nombreSelect.replace('medico_', '');
                    medicosAsignados[enfermedad] = select.value;
                }
            }
        });
        
        const datosPaciente = {
            dni: formData.get('dni').trim(),
            nombres: formData.get('nombres').trim(),
            apellidos: formData.get('apellidos').trim(),
            fecha_nacimiento: formData.get('fecha_nacimiento'),
            email: formData.get('email').trim(),
            telefono: formData.get('telefono').trim() || null,
            direccion: formData.get('direccion').trim() || null,
            enfermedades: enfermedadesSeleccionadas,
            medicos_asignados: medicosAsignados 
        };
        
        guardarNuevoPaciente.disabled = true;
        guardarNuevoPaciente.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creando...';
        
        fetch('/admin/pacientes/api/crear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(datosPaciente)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('🟢 Paciente creado exitosamente');
                cerrarModalNuevoPaciente();
                location.reload();
            } else {
                alert('🔴 Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('🔴 Error de conexión al servidor');
        })
        .finally(() => {
            guardarNuevoPaciente.disabled = false;
            guardarNuevoPaciente.innerHTML = '<i class="fas fa-save"></i> Crear Paciente';
        });
    }

    function validarFormularioNuevoPaciente() {
        const nombres = document.getElementById('nuevoNombres').value.trim();
        const apellidos = document.getElementById('nuevoApellidos').value.trim();
        const dni = document.getElementById('nuevoDni').value.trim();
        const fechaNacimiento = document.getElementById('nuevoFechaNacimiento').value;
        const email = document.getElementById('nuevoEmail').value.trim();
        
        if (!nombres) {
            alert('El campo Nombres es obligatorio');
            document.getElementById('nuevoNombres').focus();
            return false;
        }
        
        if (!apellidos) {
            alert('El campo Apellidos es obligatorio');
            document.getElementById('nuevoApellidos').focus();
            return false;
        }
        
        if (!dni || dni.length !== 8) {
            alert('El DNI debe tener exactamente 8 dígitos');
            document.getElementById('nuevoDni').focus();
            return false;
        }
        
        if (!fechaNacimiento) {
            alert('La fecha de nacimiento es obligatoria');
            document.getElementById('nuevoFechaNacimiento').focus();
            return false;
        }
        
        if (!email) {
            alert('El campo Email es obligatorio');
            document.getElementById('nuevoEmail').focus();
            return false;
        }
        
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert('Por favor ingrese un email válido');
            document.getElementById('nuevoEmail').focus();
            return false;
        }
        
        const fechaSeleccionada = new Date(fechaNacimiento);
        const hoy = new Date();
        if (fechaSeleccionada > hoy) {
            alert('La fecha de nacimiento no puede ser una fecha futura');
            document.getElementById('nuevoFechaNacimiento').focus();
            return false;
        }
        
        return true;
    }

    // ========================
    // MODAL CUIDADOR
    // ========================
    function cerrarModalCuidador() {
        if (modalCuidador) {
            modalCuidador.style.display = 'none';
            if (formCuidador) {
                formCuidador.reset();
            }
        }
    }

    function guardarCuidadorHandler() {
        if (!formCuidador) return;
        
        const formData = new FormData(formCuidador);
        const pacienteId = modalCuidador.dataset.pacienteId;
        const pacienteNombre = modalCuidador.dataset.pacienteNombre;
        
        const nombre = document.getElementById('cuidadorNombre').value.trim();
        const dni = document.getElementById('cuidadorDNI').value.trim();
        const telefono = document.getElementById('cuidadorTelefono').value.trim();
        const relacion = document.getElementById('cuidadorRelacion').value;
        
        if (!nombre || !dni || !telefono || !relacion) {
            alert('Por favor, complete todos los campos obligatorios.');
            return;
        }
        
        if (dni.length !== 8) {
            alert('El DNI debe tener exactamente 8 dígitos.');
            return;
        }
        
        console.log('Guardando cuidador:', {
            pacienteId,
            pacienteNombre,
            nombre,
            dni,
            telefono,
            relacion
        });
        
        alert(`Cuidador ${nombre} asignado exitosamente a ${pacienteNombre}`);
        cerrarModalCuidador();
    }

    // ========================
    // FUNCIONES AUXILIARES
    // ========================
    function obtenerEspecialidadPorEnfermedad(enfermedad) {
        const especialidades = {
            'diabetes': 'ENDOCRINOLOGÍA',
            'hipertension': 'MEDICINA INTERNA',
            'asma': 'NEUMOLOGÍA',
            'cardiovascular': 'CARDIOLOGÍA'
        };
        return especialidades[enfermedad] || '';
    }

    function configurarValidacionesBasicas() {
        const dniInput = document.getElementById('editDni');
        if (dniInput) {
            dniInput.addEventListener('input', function() {
                this.value = this.value.replace(/[^0-9]/g, '').substring(0, 8);
            });
        }
        
        const nombresInput = document.getElementById('editNombres');
        const apellidosInput = document.getElementById('editApellidos');
        
        [nombresInput, apellidosInput].forEach(input => {
            if (input) {
                input.addEventListener('input', function() {
                    this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '');
                });
            }
        });

        const telefonoInput = document.getElementById('editTelefono');
        if (telefonoInput) {
            telefonoInput.addEventListener('input', function() {
                this.value = this.value.replace(/[^0-9]/g, '').substring(0, 9);
            });
        }
        
        const cuidadorDni = document.getElementById('cuidador_dni');
        if (cuidadorDni) {
            cuidadorDni.addEventListener('input', function() {
                this.value = this.value.replace(/[^0-9]/g, '').substring(0, 8);
            });
        }

        const cuidadorTelefono = document.getElementById('cuidador_telefono');
        if (cuidadorTelefono) {
            cuidadorTelefono.addEventListener('input', function() {
                this.value = this.value.replace(/[^0-9]/g, '').substring(0, 9);
            });
        }
    }

    function cargarMedicosParaEdicion(paciente) {
        fetch('/admin/pacientes/api/medicos')
            .then(response => response.json())
            .then(data => {
                if (data.medicos) {
                    window.medicosDisponibles = data.medicos;
                    actualizarSelectoresMedicos(paciente.medicos_asignados);
                    
                    const checkboxes = document.querySelectorAll('input[name="enfermedades"]');
                    checkboxes.forEach(checkbox => {
                        checkbox.addEventListener('change', function() {
                            actualizarSelectoresMedicos(paciente.medicos_asignados);
                        });
                    });
                }
            })
            .catch(error => {
                console.error('Error al cargar médicos:', error);
            });
    }

    function actualizarSelectoresMedicos(medicosActuales = []) {
        const checkboxesSeleccionados = document.querySelectorAll('input[name="enfermedades"]:checked');
        const contenedor = document.getElementById('contenedorMedicosPorEnfermedad');
        
        contenedor.innerHTML = '';
        
        if (checkboxesSeleccionados.length === 0) {
            contenedor.innerHTML = '<p class="text-muted">Seleccione las enfermedades para asignar médicos...</p>';
            return;
        }
        
        checkboxesSeleccionados.forEach(checkbox => {
            const enfermedad = checkbox.value;
            const especialidad = checkbox.getAttribute('data-especialidad');
            
            const medicosEspecialidad = window.medicosDisponibles.filter(medico => 
                medico.especialidad === especialidad
            );
            
            const medicoActual = medicosActuales.find(m => 
                m.enfermedad && m.enfermedad.toLowerCase() === enfermedad.toLowerCase()
            );
            
            const selectHTML = `
                <div class="medico-enfermedad">
                    <label><strong>Médico para ${enfermedad}:</strong></label>
                    <select name="medico_${enfermedad}" class="form-control">
                        <option value="">Seleccionar médico...</option>
                        ${medicosEspecialidad.map(medico => 
                            `<option value="${medico.id}" ${medico.id == (medicoActual ? medicoActual.id : '') ? 'selected' : ''}>
                                Dr. ${medico.nombre_formal} - ${especialidad}
                            </option>`
                        ).join('')}
                    </select>
                    <small class="text-muted">Especialidad: ${especialidad}</small>
                </div>
            `;
            
            contenedor.insertAdjacentHTML('beforeend', selectHTML);
        });
    }

    function configurarEventosCuidador() {
        const btnAgregar = document.getElementById('agregarCuidador');
        if (btnAgregar) {
            btnAgregar.addEventListener('click', mostrarFormularioCuidador);
        }
        
        const btnEliminar = document.querySelector('.btn-eliminar-cuidador');
        if (btnEliminar) {
            btnEliminar.addEventListener('click', eliminarCuidador);
        }
    }

    function mostrarFormularioCuidador() {
        const container = document.getElementById('cuidador-container');
        
        container.innerHTML = `
            <div class="nuevo-cuidador">
                <h5>Nuevo Cuidador</h5>
                <div class="form-grid">
                    <div class="form-group">
                        <label for="cuidador_nombre">Nombre completo *</label>
                        <input type="text" id="cuidador_nombre" name="cuidador_nombre" required>
                    </div>
                    <div class="form-group">
                        <label for="cuidador_dni">DNI *</label>
                        <input type="text" id="cuidador_dni" name="cuidador_dni" required maxlength="8">
                    </div>
                    <div class="form-group">
                        <label for="cuidador_telefono">Teléfono *</label>
                        <input type="tel" id="cuidador_telefono" name="cuidador_telefono" required>
                    </div>
                    <div class="form-group">
                        <label for="cuidador_relacion">Relación *</label>
                        <select id="cuidador_relacion" name="cuidador_relacion" required>
                            <option value="">Seleccionar...</option>
                            <option value="hijo">Hijo/a</option>
                            <option value="padre">Padre/Madre</option>
                            <option value="hermano">Hermano/a</option>
                            <option value="conyugue">Cónyuge</option>
                            <option value="familiar">Otro familiar</option>
                            <option value="amigo">Amistad</option>
                            <option value="profesional">Cuidador profesional</option>
                            <option value="otro">Otro</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <button type="button" class="btn-cancelar-cuidador">
                            <i class="fas fa-times"></i> Cancelar
                        </button>
                    </div>
                </div>
                <input type="hidden" name="cuidador_id" value="nuevo">
            </div>
        `;
        
        configurarValidacionesBasicas();
        
        container.querySelector('.btn-cancelar-cuidador').addEventListener('click', function() {
            container.innerHTML = `
                <div class="sin-cuidador">
                    <p>Este paciente no tiene cuidador registrado.</p>
                    <button type="button" id="agregarCuidador" class="btn btn-outline">
                        <i class="fas fa-plus"></i> Agregar cuidador
                    </button>
                </div>
            `;
            configurarEventosCuidador();
        });
    }

    function eliminarCuidador() {
        if (confirm('¿Está seguro de que desea eliminar este cuidador?')) {
            const container = document.getElementById('cuidador-container');
            
            container.innerHTML = `
                <div class="sin-cuidador">
                    <p>Este paciente no tiene cuidador registrado.</p>
                    <button type="button" id="agregarCuidador" class="btn btn-outline">
                        <i class="fas fa-plus"></i> Agregar cuidador
                    </button>
                </div>
                <input type="hidden" name="eliminar_cuidador" value="true">
            `;
            
            configurarEventosCuidador();
        }
    }

    function validarFormularioEdicion(form) {
        const nombres = form.querySelector('#editNombres').value.trim();
        const apellidos = form.querySelector('#editApellidos').value.trim();
        const dni = form.querySelector('#editDni').value.trim();
        const fechaNacimiento = form.querySelector('#editFechaNacimiento').value;
        
        if (!nombres) {
            alert('El campo Nombres es obligatorio');
            form.querySelector('#editNombres').focus();
            return false;
        }
        
        if (!apellidos) {
            alert('El campo Apellidos es obligatorio');
            form.querySelector('#editApellidos').focus();
            return false;
        }
        
        if (!dni || dni.length !== 8) {
            alert('El DNI debe tener exactamente 8 dígitos');
            form.querySelector('#editDni').focus();
            return false;
        }
        
        if (!fechaNacimiento) {
            alert('La fecha de nacimiento es obligatoria');
            form.querySelector('#editFechaNacimiento').focus();
            return false;
        }
        
        const fechaSeleccionada = new Date(fechaNacimiento);
        const hoy = new Date();
        if (fechaSeleccionada > hoy) {
            alert('La fecha de nacimiento no puede ser una fecha futura');
            form.querySelector('#editFechaNacimiento').focus();
            return false;
        }
        
        const cuidadorNombre = form.querySelector('#cuidador_nombre');
        if (cuidadorNombre && cuidadorNombre.value.trim()) {
            if (!form.querySelector('#cuidador_dni').value.trim() || 
                form.querySelector('#cuidador_dni').value.length !== 8) {
                alert('El DNI del cuidador debe tener 8 dígitos');
                form.querySelector('#cuidador_dni').focus();
                return false;
            }
            
            if (!form.querySelector('#cuidador_telefono').value.trim()) {
                alert('El teléfono del cuidador es obligatorio');
                form.querySelector('#cuidador_telefono').focus();
                return false;
            }
            
            if (!form.querySelector('#cuidador_relacion').value) {
                alert('La relación del cuidador es obligatoria');
                form.querySelector('#cuidador_relacion').focus();
                return false;
            }
        }
        
        return true;
    }

    // ========================
    // PAGINACIÓN
    // ========================
    document.addEventListener('click', function(e) {
        if (e.target.closest('.btn-page')) {
            const pageBtn = e.target.closest('.btn-page');
            
            document.querySelectorAll('.btn-page').forEach(btn => {
                btn.classList.remove('active');
            });
            
            pageBtn.classList.add('active');
            
            const pageNumber = pageBtn.textContent;
            console.log(`Cargar página: ${pageNumber}`);
        }
        
        if (e.target.closest('.btn-pagination')) {
            const paginationBtn = e.target.closest('.btn-pagination');
            const isNext = paginationBtn.textContent.includes('Siguiente');
            
            console.log(`Navegación: ${isNext ? 'Siguiente' : 'Anterior'}`);
        }
    });

    // ========================
    // FUNCIÓN CAMBIAR COLOR
    // ========================
    function cambiar_color() {
        var estados = document.querySelectorAll(".estado");
        
        estados.forEach(function(estado) {
            estado.classList.add("status");
            
            var texto = estado.innerText.trim().toUpperCase();
            
            if (texto === "ACTIVO") {
                estado.classList.add("active");
            } else if (texto === "INACTIVO") {
                estado.classList.add("inactive");
            }
        });
    }

    // Ejecutar al cargar
    cambiar_color();
});