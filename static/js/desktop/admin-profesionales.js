// static/js/desktop/admin-profesionales.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('Página de Profesionales cargada');

    // ========================
    // ELEMENTOS DEL DOM
    // ========================
    const busquedaInput = document.getElementById('busquedaInput');
    const especialidadFilter = document.getElementById('especialidadFilter');
    const rolFilter = document.getElementById('rolFilter');
    const estadoFilter = document.getElementById('estadoFilter');
    const profesionalesTable = document.getElementById('profesionalesTable');
    const nuevoProfesionalBtn = document.getElementById('nuevoProfesionalBtn');
    
    // Modal Profesional
    const modalProfesional = document.getElementById('modalProfesional');
    const closeProfesionalModal = document.getElementById('closeProfesionalModal');
    const cancelProfesional = document.getElementById('cancelProfesional');
    const guardarProfesional = document.getElementById('guardarProfesional');
    const formProfesional = document.getElementById('formProfesional');
    const modalTitle = document.getElementById('modalTitle');

    // Campos del formulario
    const profRol = document.getElementById('profRol');
    const profEspecialidad = document.getElementById('profEspecialidad');
    const profDNI = document.getElementById('profDNI');
    const profUsuario = document.getElementById('profUsuario');

    // Variables para paginación y filtros
    let currentPage = 1;
    let currentFilters = {
        especialidad: 'todas',
        rol: 'todos',
        estado: 'todos',
        busqueda: ''
    };

    // Variables modales dinámicos
    let modalVerProfesional = null;
    let modalEditarProfesional = null;

    // ========================
    // FUNCIONALIDAD DE FILTROS CON BACKEND
    // ========================
    
    // Búsqueda en tiempo real con debounce
    let searchTimeout;
    busquedaInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentFilters.busqueda = this.value.trim();
            currentPage = 1;
            cargarProfesionales();
        }, 300);
    });

    // Filtros por select
    especialidadFilter.addEventListener('change', function() {
        currentFilters.especialidad = this.value;
        currentPage = 1;
        cargarProfesionales();
    });

    rolFilter.addEventListener('change', function() {
        currentFilters.rol = this.value;
        currentPage = 1;
        cargarProfesionales();
    });

    estadoFilter.addEventListener('change', function() {
        currentFilters.estado = this.value;
        currentPage = 1;
        cargarProfesionales();
    });

    // ========================
    // FUNCIÓN PRINCIPAL: CARGAR PROFESIONALES DESDE BACKEND
    // ========================
    function cargarProfesionales() {
        console.log('Cargando profesionales desde el servidor...');
        
        // Construir parámetros de la URL
        const params = new URLSearchParams({
            especialidad: currentFilters.especialidad,
            rol: currentFilters.rol,
            estado: currentFilters.estado,
            page: currentPage,
            per_page: 10
        });

        if (currentFilters.busqueda) {
            params.append('busqueda', currentFilters.busqueda);
        }

        // Mostrar indicador de carga
        mostrarCargandoTabla();

        // Hacer petición al backend
        fetch(`/admin/profesionales/api/listar?${params}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Profesionales cargados:', data);
                actualizarTablaProfesionales(data.profesionales);
                actualizarPaginacion(data);
                actualizarContadorResultados(data);
            })
            .catch(error => {
                console.error('Error al cargar profesionales:', error);
                mostrarErrorTabla('Error al cargar los profesionales: ' + error.message);
            });
    }

    function mostrarCargandoTabla() {
        const tbody = profesionalesTable.querySelector('tbody');
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center">
                    <div class="loading-container">
                        <div class="loading-spinner"></div>
                        <span>Cargando profesionales...</span>
                    </div>
                </td>
            </tr>
        `;
    }

    function mostrarErrorTabla(mensaje) {
        const tbody = profesionalesTable.querySelector('tbody');
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>${mensaje}</span>
                </td>
            </tr>
        `;
    }

    function actualizarTablaProfesionales(profesionales) {
        const tbody = profesionalesTable.querySelector('tbody');
        
        if (!profesionales || profesionales.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center">No hay profesionales que coincidan con los filtros</td>
                </tr>
            `;
            return;
        }

        const filas = profesionales.map(prof => {
            return `
                <tr data-id="${prof.id}">
                    <td>${prof.id}</td>
                    <td>${prof.nombre_completo}</td>
                    <td>${prof.dni}</td>
                    <td>
                        <span class="especialidad-tag ${convertirClaseEspecialidad(prof.especialidad)}">
                            ${prof.especialidad}
                        </span>
                    </td>
                    <td>
                        <span class="rol-tag ${prof.rol.toLowerCase()}">${prof.rol}</span>
                    </td>
                    <td>${prof.horario_atencion}</td>
                    <td>
                        <span class="pacientes-count">${prof.pacientes_asignados}</span>
                        <small>${prof.rol === 'PSICÓLOGO' ? 'sesiones' : 'pacientes'}</small>
                    </td>
                    <td>
                        <span class="status ${prof.estado.toLowerCase()}">${prof.estado}</span>
                    </td>
                    <td>
                        <div class="action-buttons">
                            <button class="btn-action btn-view" title="Ver detalles" data-id="${prof.id}">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn-action btn-edit" title="Editar" data-id="${prof.id}">
                                <i class="fas fa-edit"></i>
                            </button>
                            ${prof.rol === 'MÉDICO' ? 
                                `<button class="btn-action btn-schedule" title="Gestionar Horarios" data-id="${prof.id}">
                                    <i class="fas fa-calendar-alt"></i>
                                </button>` :
                                `<button class="btn-action btn-forum" title="Estadísticas Foro" data-id="${prof.id}">
                                    <i class="fas fa-comments"></i>
                                </button>`
                            }
                            <button class="btn-action btn-toggle ${prof.estado === 'ACTIVO' ? 'active' : 'inactive'}" 
                                    title="Activar/Desactivar" data-id="${prof.id}">
                                <i class="fas ${prof.estado === 'ACTIVO' ? 'fa-toggle-on' : 'fa-toggle-off'}"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');

        tbody.innerHTML = filas;
    }

    function convertirClaseEspecialidad(especialidad) {
        const mapa = {
            'CARDIOLOGÍA': 'cardiologia',
            'MEDICINA INTERNA': 'medicina-interna',
            'ENDOCRINOLOGÍA': 'endocrinologia',
            'PSICOLOGÍA CLÍNICA': 'psicologia',
            'NEUMOLOGÍA': 'neumologia'
        };
        return mapa[especialidad] || 'general';
    }

    function actualizarPaginacion(data) {
        const paginationWrapper = document.querySelector('.pagination-wrapper');
        if (!paginationWrapper) return;

        let paginationHTML = '';
        
        if (data.pages > 1) {
            paginationHTML = `
                <div class="pagination-controls">
                    <button class="btn-pagination ${!data.has_prev ? 'disabled' : ''}" 
                            onclick="cambiarPagina(${currentPage - 1})" 
                            ${!data.has_prev ? 'disabled' : ''}>
                        <i class="fas fa-chevron-left"></i> Anterior
                    </button>
                    <span class="pagination-pages">
                        ${generarBotonesPagina(data.current_page, data.pages)}
                    </span>
                    <button class="btn-pagination ${!data.has_next ? 'disabled' : ''}" 
                            onclick="cambiarPagina(${currentPage + 1})" 
                            ${!data.has_next ? 'disabled' : ''}>
                        Siguiente <i class="fas fa-chevron-right"></i>
                    </button>
                </div>
            `;
        }

        // Buscar si ya existe la sección de controles o crear una nueva
        let controlsDiv = paginationWrapper.querySelector('.pagination-controls');
        if (controlsDiv) {
            controlsDiv.outerHTML = paginationHTML;
        } else {
            paginationWrapper.insertAdjacentHTML('beforeend', paginationHTML);
        }
    }

    function generarBotonesPagina(actual, total) {
        let botones = '';
        
        for (let i = 1; i <= total; i++) {
            if (i === actual) {
                botones += `<button class="btn-page active">${i}</button>`;
            } else if (i <= 3 || i > total - 3 || Math.abs(i - actual) <= 1) {
                botones += `<button class="btn-page" onclick="cambiarPagina(${i})">${i}</button>`;
            } else if (i === 4 && actual > 6) {
                botones += `<span>...</span>`;
            } else if (i === total - 3 && actual < total - 5) {
                botones += `<span>...</span>`;
            }
        }
        
        return botones;
    }

    function actualizarContadorResultados(data) {
        const paginationInfo = document.querySelector('.pagination-info');
        if (paginationInfo) {
            const inicio = (data.current_page - 1) * data.per_page + 1;
            const fin = Math.min(data.current_page * data.per_page, data.total);
            paginationInfo.textContent = `Mostrando ${inicio}-${fin} de ${data.total} profesionales`;
        }
    }

    // Función global para cambiar página
    window.cambiarPagina = function(nuevaPagina) {
        currentPage = nuevaPagina;
        cargarProfesionales();
    };

    // ========================
    // ACCIONES DE LA TABLA CON BACKEND
    // ========================
    
    profesionalesTable.addEventListener('click', function(e) {
        const target = e.target.closest('.btn-action');
        if (!target) return;
        
        const profesionalId = target.dataset.id;
        const row = target.closest('tr');
        const profesionalNombre = row.cells[1].textContent;
        
        if (target.classList.contains('btn-view')) {
            verProfesional(profesionalId, profesionalNombre);
        } else if (target.classList.contains('btn-edit')) {
            editarProfesional(profesionalId, profesionalNombre);
        } else if (target.classList.contains('btn-schedule')) {
            gestionarHorarios(profesionalId, profesionalNombre);
        } else if (target.classList.contains('btn-forum')) {
            estadisticasForo(profesionalId, profesionalNombre);
        } else if (target.classList.contains('btn-toggle')) {
            toggleEstadoProfesional(target, row, profesionalId);
        }
    });

    function verProfesional(id, nombre) {
        console.log(`Ver detalles del profesional: ${nombre} (ID: ${id})`);
        
        // Crear modal dinámico si no existe
        if (!modalVerProfesional) {
            crearModalVerProfesional();
        }
        
        mostrarLoadingProfesional();
        modalVerProfesional.style.display = 'block';
        
        // Cargar datos del profesional
        fetch(`/admin/profesionales/api/${id}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    mostrarDetallesProfesional(data.profesional);
                } else {
                    mostrarErrorProfesional(data.message || 'Error al cargar los datos');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarErrorProfesional('Error de conexión: ' + error.message);
            });
    }

    function editarProfesional(id, nombre) {
        console.log(`Editar profesional: ${nombre} (ID: ${id})`);
        
        // Cambiar título del modal
        modalTitle.textContent = `Editar Profesional - ${nombre}`;
        
        // Cargar datos del profesional para edición
        fetch(`/admin/profesionales/api/${id}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    cargarDatosFormulario(data.profesional);
                    modalProfesional.style.display = 'block';
                    modalProfesional.dataset.modo = 'editar';
                    modalProfesional.dataset.profesionalId = id;
                } else {
                    alert('Error al cargar datos del profesional: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al cargar datos del profesional');
            });
    }

    function toggleEstadoProfesional(button, row, id) {
        const statusSpan = row.querySelector('.status');
        const isActive = statusSpan.classList.contains('active');
        
        // Deshabilitar botón temporalmente
        button.disabled = true;
        button.style.opacity = '0.6';
        
        // Hacer petición al servidor
        fetch(`/admin/profesionales/api/${id}/toggle-estado`, {
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
                // Actualizar estado visual
                const nuevoEstado = data.nuevo_estado;
                const esActivo = nuevoEstado === 'ACTIVO';
                
                statusSpan.classList.toggle('active', esActivo);
                statusSpan.classList.toggle('inactive', !esActivo);
                statusSpan.textContent = nuevoEstado;
                
                button.classList.toggle('active', esActivo);
                button.classList.toggle('inactive', !esActivo);
                button.querySelector('i').className = `fas fa-toggle-${esActivo ? 'on' : 'off'}`;
                
                console.log(`Estado del profesional ${id} cambiado a: ${nuevoEstado}`);
                
                // Mostrar mensaje de éxito
                mostrarNotificacion(data.message, 'success');
            } else {
                console.error('Error del servidor:', data.message);
                mostrarNotificacion('Error: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarNotificacion('Error de conexión: ' + error.message, 'error');
        })
        .finally(() => {
            button.disabled = false;
            button.style.opacity = '1';
        });
    }

    // ========================
    // MODAL PROFESIONAL CON BACKEND
    // ========================
    
    // Abrir modal para nuevo profesional
    nuevoProfesionalBtn.addEventListener('click', function() {
        modalTitle.textContent = 'Nuevo Profesional';
        formProfesional.reset();
        deshabilitarHorarios();
        modalProfesional.style.display = 'block';
        modalProfesional.dataset.modo = 'nuevo';
        limpiarValidaciones();
    });

    // Cerrar modal
    function cerrarModalProfesional() {
        modalProfesional.style.display = 'none';
        formProfesional.reset();
        limpiarValidaciones();
        delete modalProfesional.dataset.profesionalId;
    }

    closeProfesionalModal.addEventListener('click', cerrarModalProfesional);
    cancelProfesional.addEventListener('click', cerrarModalProfesional);

    // Cerrar modal al hacer clic en el overlay
    modalProfesional.addEventListener('click', function(e) {
        if (e.target === modalProfesional || e.target.classList.contains('modal-overlay')) {
            cerrarModalProfesional();
        }
    });

    // ========================
    // GUARDAR PROFESIONAL CON BACKEND
    // ========================
    
    guardarProfesional.addEventListener('click', function() {
        if (validarFormulario()) {
            guardarDatos();
        }
    });

    function guardarDatos() {
        const modo = modalProfesional.dataset.modo;
        const profesionalId = modalProfesional.dataset.profesionalId;
        
        // Recopilar datos del formulario
        const datos = recopilarDatosFormulario();
        
        console.log(`${modo === 'nuevo' ? 'Crear' : 'Actualizar'} profesional:`, datos);
        
        // Deshabilitar botón de guardar
        guardarProfesional.disabled = true;
        guardarProfesional.textContent = 'Guardando...';
        
        const url = modo === 'nuevo' 
            ? '/admin/profesionales/api/crear'
            : `/admin/profesionales/api/${profesionalId}/actualizar`;
            
        const method = modo === 'nuevo' ? 'POST' : 'PUT';
        
        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(datos)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                mostrarNotificacion(data.message, 'success');
                cerrarModalProfesional();
                
                // Recargar la tabla
                cargarProfesionales();
            } else {
                mostrarNotificacion('Error: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarNotificacion('Error de conexión: ' + error.message, 'error');
        })
        .finally(() => {
            guardarProfesional.disabled = false;
            guardarProfesional.textContent = 'Guardar Profesional';
        });
    }

    function recopilarDatosFormulario() {
        // Dividir el nombre completo en nombres y apellidos
        const nombreCompleto = document.getElementById('profNombre').value.trim();
        const partesNombre = nombreCompleto.split(' ');
        const nombres = partesNombre.slice(0, 2).join(' '); // Primeros 2 como nombres
        const apellidos = partesNombre.slice(2).join(' ') || partesNombre[1] || ''; // Resto como apellidos

        return {
            dni: profDNI.value.trim(),
            nombres: nombres,
            apellidos: apellidos,
            telefono: document.getElementById('profTelefono').value.trim(),
            email: document.getElementById('profEmail').value.trim(),
            rol: profRol.value,
            especialidad: profEspecialidad.value,
            horarios: obtenerHorarios()
        };
    }

    function obtenerHorarios() {
        const horarios = {};
        const diasSemana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes'];
        
        diasSemana.forEach(dia => {
            const checkbox = document.getElementById(dia);
            if (checkbox && checkbox.checked) {
                const inicio = document.getElementById(dia + 'Inicio').value;
                const fin = document.getElementById(dia + 'Fin').value;
                
                if (inicio && fin) {
                    horarios[`${dia}_activo`] = true;
                    horarios[`${dia}_inicio`] = inicio;
                    horarios[`${dia}_fin`] = fin;
                }
            }
        });
        
        return horarios;
    }

    // ========================
    // FUNCIONES AUXILIARES Y MODALES DINÁMICOS
    // ========================

    function crearModalVerProfesional() {
        const modalHTML = `
            <div id="modalVerProfesional" class="modal-container" style="display: none;">
                <div class="modal">
                    <div class="modal-header">
                        <h3>Detalles del Profesional</h3>
                        <button type="button" class="close-btn" id="closeVerProfesionalModal">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <div id="profesionalDetallesContent">
                            <!-- Contenido dinámico -->
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" id="cerrarVerProfesional">
                            <i class="fas fa-times"></i> Cerrar
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        modalVerProfesional = document.getElementById('modalVerProfesional');
        
        // Configurar eventos
        document.getElementById('closeVerProfesionalModal').addEventListener('click', () => {
            modalVerProfesional.style.display = 'none';
        });
        document.getElementById('cerrarVerProfesional').addEventListener('click', () => {
            modalVerProfesional.style.display = 'none';
        });
    }

    function mostrarLoadingProfesional() {
        const content = document.getElementById('profesionalDetallesContent');
        if (content) {
            content.innerHTML = `
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <p>Cargando información del profesional...</p>
                </div>
            `;
        }
    }

    function mostrarErrorProfesional(mensaje) {
        const content = document.getElementById('profesionalDetallesContent');
        if (content) {
            content.innerHTML = `
                <div class="error-container">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p class="error-message">${mensaje}</p>
                </div>
            `;
        }
    }

    function mostrarDetallesProfesional(profesional) {
        const content = document.getElementById('profesionalDetallesContent');
        
        const pacientesHTML = profesional.pacientes_asignados && profesional.pacientes_asignados.length > 0 
            ? profesional.pacientes_asignados.map(paciente => `
                <div class="paciente-item">
                    <div class="paciente-info">
                        <h4>${paciente.nombre_completo}</h4>
                        <p><strong>DNI:</strong> ${paciente.dni}</p>
                        <p><strong>Enfermedad:</strong> ${paciente.enfermedad}</p>
                        <p><strong>Fecha asignación:</strong> ${paciente.fecha_asignacion}</p>
                        ${paciente.observaciones ? `<p><strong>Observaciones:</strong> ${paciente.observaciones}</p>` : ''}
                    </div>
                </div>
            `).join('')
            : '<p class="no-data">No tiene pacientes asignados</p>';
        
        content.innerHTML = `
            <div class="profesional-detalle">
                <!-- Información Personal -->
                <div class="detalle-seccion">
                    <h3><i class="fas fa-user"></i> Información Personal</h3>
                    <div class="detalle-grid">
                        <div class="detalle-item">
                            <label>Nombre completo:</label>
                            <span>${profesional.nombre_completo}</span>
                        </div>
                        <div class="detalle-item">
                            <label>DNI:</label>
                            <span>${profesional.dni}</span>
                        </div>
                        <div class="detalle-item">
                            <label>Email:</label>
                            <span>${profesional.email || 'No registrado'}</span>
                        </div>
                        <div class="detalle-item">
                            <label>Teléfono:</label>
                            <span>${profesional.telefono || 'No registrado'}</span>
                        </div>
                        <div class="detalle-item">
                            <label>Estado:</label>
                            <span class="status ${profesional.estado.toLowerCase()}">${profesional.estado}</span>
                        </div>
                        <div class="detalle-item">
                            <label>Fecha de registro:</label>
                            <span>${profesional.fecha_registro}</span>
                        </div>
                    </div>
                </div>

                <!-- Información Profesional -->
                <div class="detalle-seccion">
                    <h3><i class="fas fa-stethoscope"></i> Información Profesional</h3>
                    <div class="detalle-grid">
                        <div class="detalle-item">
                            <label>Rol:</label>
                            <span class="rol-tag ${profesional.rol.toLowerCase()}">${profesional.rol}</span>
                        </div>
                        <div class="detalle-item">
                            <label>Especialidad:</label>
                            <span class="especialidad-tag">${profesional.especialidad}</span>
                        </div>
                        <div class="detalle-item full-width">
                            <label>Horarios de atención:</label>
                            <span>${profesional.horario_atencion || 'No definido'}</span>
                        </div>
                    </div>
                </div>

                <!-- Pacientes Asignados -->
                <div class="detalle-seccion">
                    <h3><i class="fas fa-users"></i> Pacientes Asignados (${profesional.pacientes_asignados_count})</h3>
                    <div class="pacientes-lista">
                        ${pacientesHTML}
                    </div>
                </div>
            </div>
        `;
    }

    function mostrarNotificacion(mensaje, tipo) {
        // Crear notificación temporal
        const notificacion = document.createElement('div');
        notificacion.className = `notificacion ${tipo}`;
        notificacion.innerHTML = `
            <i class="fas fa-${tipo === 'success' ? 'check' : 'exclamation-triangle'}"></i>
            <span>${mensaje}</span>
        `;
        
        document.body.appendChild(notificacion);
        
        // Animar entrada
        setTimeout(() => notificacion.classList.add('show'), 100);
        
        // Remover después de 3 segundos
        setTimeout(() => {
            notificacion.classList.remove('show');
            setTimeout(() => document.body.removeChild(notificacion), 300);
        }, 3000);
    }

    // ========================
    // MANTENER FUNCIONES EXISTENTES
    // ========================
    
    // Validación DNI en tiempo real
    profDNI.addEventListener('input', function() {
        this.value = this.value.replace(/[^0-9]/g, '').substring(0, 8);
        validarDNI();
    });

    function validarDNI() {
        const dni = profDNI.value;
        
        if (dni.length === 0) {
            mostrarError(profDNI, '');
            return false;
        } else if (dni.length !== 8) {
            mostrarError(profDNI, 'El DNI debe tener 8 dígitos');
            return false;
        } else {
            mostrarExito(profDNI, 'DNI válido');
            return true;
        }
    }

    // Generar usuario automáticamente
    profRol.addEventListener('change', generarUsuario);
    document.getElementById('profNombre').addEventListener('input', generarUsuario);

    function generarUsuario() {
        const nombre = document.getElementById('profNombre').value.trim();
        const rol = profRol.value;
        
        if (nombre && rol) {
            const nombres = nombre.toLowerCase().split(' ');
            let usuario = '';
            
            if (rol === 'MÉDICO') {
                usuario = 'dr.' + (nombres[0] || '') + '.' + (nombres[2] || nombres[1] || '');
            } else if (rol === 'PSICÓLOGO') {
                usuario = 'psic.' + (nombres[0] || '') + '.' + (nombres[2] || nombres[1] || '');
            }
            
            usuario = usuario.replace(/[^a-z.]/g, '').substring(0, 20);
            profUsuario.value = usuario;
        }
    }

    // ========================
    // GESTIÓN DE HORARIOS
    // ========================
    
    // Habilitar/deshabilitar campos de horario según checkbox
    const diasSemana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes'];
    
    diasSemana.forEach(dia => {
        const checkbox = document.getElementById(dia);
        const inicioInput = document.getElementById(dia + 'Inicio');
        const finInput = document.getElementById(dia + 'Fin');
        
        if (checkbox && inicioInput && finInput) {
            checkbox.addEventListener('change', function() {
                const isChecked = this.checked;
                inicioInput.disabled = !isChecked;
                finInput.disabled = !isChecked;
                
                if (!isChecked) {
                    inicioInput.value = '';
                    finInput.value = '';
                }
            });
        }
    });

    function deshabilitarHorarios() {
        diasSemana.forEach(dia => {
            const checkbox = document.getElementById(dia);
            const inicioInput = document.getElementById(dia + 'Inicio');
            const finInput = document.getElementById(dia + 'Fin');
            
            if (checkbox && inicioInput && finInput) {
                checkbox.checked = false;
                inicioInput.disabled = true;
                finInput.disabled = true;
                inicioInput.value = '';
                finInput.value = '';
            }
        });
    }

    function cargarDatosFormulario(profesional) {
        // Cargar datos básicos
        document.getElementById('profNombre').value = profesional.nombre_completo;
        profDNI.value = profesional.dni;
        document.getElementById('profTelefono').value = profesional.telefono || '';
        document.getElementById('profEmail').value = profesional.email || '';
        profRol.value = profesional.rol;
        profEspecialidad.value = profesional.especialidad;
        
        // Cargar horarios si existen
        if (profesional.horario_atencion) {
            cargarHorarios(profesional.horario_atencion);
        }
        
        // Generar usuario basado en los datos
        generarUsuario();
    }

    function cargarHorarios(horarios) {
        if (typeof horarios === 'string') {
            try {
                horarios = JSON.parse(horarios);
            } catch (e) {
                console.error('Error al parsear horarios:', e);
                return;
            }
        }
        
        diasSemana.forEach(dia => {
            const checkbox = document.getElementById(dia);
            const inicioInput = document.getElementById(dia + 'Inicio');
            const finInput = document.getElementById(dia + 'Fin');
            
            if (horarios[dia] && horarios[dia] !== 'No disponible' && checkbox && inicioInput && finInput) {
                const horario = horarios[dia];
                if (horario.includes('-')) {
                    const [inicio, fin] = horario.split('-');
                    checkbox.checked = true;
                    inicioInput.disabled = false;
                    finInput.disabled = false;
                    inicioInput.value = inicio.trim();
                    finInput.value = fin.trim();
                }
            }
        });
    }

    // ========================
    // VALIDACIONES DEL FORMULARIO
    // ========================
    
    function validarFormulario() {
        let esValido = true;
        
        // Validar campos requeridos
        const camposRequeridos = [
            { id: 'profNombre', mensaje: 'El nombre es obligatorio' },
            { id: 'profDNI', mensaje: 'El DNI es obligatorio' },
            { id: 'profEmail', mensaje: 'El email es obligatorio' },
            { id: 'profRol', mensaje: 'El rol es obligatorio' },
            { id: 'profEspecialidad', mensaje: 'La especialidad es obligatoria' }
        ];
        
        camposRequeridos.forEach(campo => {
            const elemento = document.getElementById(campo.id);
            const valor = elemento.value.trim();
            
            if (!valor) {
                mostrarError(elemento, campo.mensaje);
                esValido = false;
            } else {
                mostrarExito(elemento, '');
            }
        });
        
        // Validar DNI específicamente
        if (!validarDNI()) {
            esValido = false;
        }
        
        // Validar email
        const email = document.getElementById('profEmail').value;
        if (email && !validarEmail(email)) {
            mostrarError(document.getElementById('profEmail'), 'Email inválido');
            esValido = false;
        }
        
        // Validar al menos un día de horario
        const tieneHorario = diasSemana.some(dia => {
            const checkbox = document.getElementById(dia);
            return checkbox && checkbox.checked;
        });
        
        if (!tieneHorario) {
            mostrarNotificacion('Debe seleccionar al menos un día de atención', 'error');
            esValido = false;
        }
        
        return esValido;
    }

    // ========================
    // FUNCIONES UTILITARIAS
    // ========================
    
    function validarEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    function mostrarError(elemento, mensaje) {
        elemento.classList.remove('success');
        elemento.classList.add('error');
        
        let errorElement = elemento.parentNode.querySelector('.field-error');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'field-error';
            elemento.parentNode.appendChild(errorElement);
        }
        
        errorElement.textContent = mensaje;
        errorElement.classList.toggle('show', mensaje !== '');
    }

    function mostrarExito(elemento, mensaje) {
        elemento.classList.remove('error');
        elemento.classList.add('success');
        
        const errorElement = elemento.parentNode.querySelector('.field-error');
        if (errorElement) {
            errorElement.classList.remove('show');
        }
    }

    function limpiarValidaciones() {
        const inputs = formProfesional.querySelectorAll('.form-input');
        inputs.forEach(input => {
            input.classList.remove('error', 'success');
        });
        
        const errors = formProfesional.querySelectorAll('.field-error');
        errors.forEach(error => {
            error.classList.remove('show');
        });
    }

    // ========================
    // FUNCIONES DE ACCIONES ESPECIALES
    // ========================
    
    function gestionarHorarios(id, nombre) {
        console.log(`Gestionar horarios: ${nombre} (ID: ${id})`);
        mostrarNotificacion(`Función de gestión de horarios para: ${nombre} (Próximamente)`, 'info');
        // Aquí puedes redirigir a una página específica de horarios
        // window.location.href = `/admin/profesionales/${id}/horarios`;
    }

    function estadisticasForo(id, nombre) {
        console.log(`Estadísticas foro: ${nombre} (ID: ${id})`);
        mostrarNotificacion(`Estadísticas del foro para: ${nombre} (Próximamente)`, 'info');
        // Aquí puedes redirigir a una página de estadísticas
        // window.location.href = `/admin/profesionales/${id}/estadisticas-foro`;
    }

    // ========================
    // INICIALIZACIÓN
    // ========================
    
    // Cargar profesionales al inicio
    cargarProfesionales();
    
    // Deshabilitar horarios inicialmente
    deshabilitarHorarios();
    
    console.log('Funcionalidades de profesionales inicializadas correctamente con backend');
});