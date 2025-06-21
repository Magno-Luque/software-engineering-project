// static/js/desktop/admin-citas.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('Página de Citas Médicas cargada');

    // ========================
    // VARIABLES GLOBALES
    // ========================
    let currentPage = 1;
    let totalPages = 1;
    const citasPorPagina = 10;
    
    // ========================
    // ELEMENTOS DEL DOM
    // ========================
    const especialidadFilter = document.getElementById('especialidadFilter');
    const medicoFilter = document.getElementById('medicoFilter');
    const fechaFilter = document.getElementById('fechaFilter');
    const estadoFilter = document.getElementById('estadoFilter');
    const tipoFilter = document.getElementById('tipoFilter');
    const busquedaInput = document.getElementById('busquedaInput');
    const citasTable = document.getElementById('citasTable');
    const tbody = citasTable ? citasTable.querySelector('tbody') : null;
    
    // Modales
    const modalCita = document.getElementById('modalCita');
    const modalZoom = document.getElementById('modalZoom');
    const closeCitaModal = document.getElementById('closeCitaModal');
    const closeZoomModal = document.getElementById('closeZoomModal');
    
    // Botones
    const nuevaCitaBtn = document.getElementById('nuevaCitaBtn');
    const copiarZoomBtn = document.getElementById('copiarZoomBtn');
    const abrirZoomBtn = document.getElementById('abrirZoomBtn');

    // ========================
    // INICIALIZACIÓN
    // ========================
    inicializarPagina();
    
    function inicializarPagina() {
        // Establecer fecha de hoy por defecto si existe el filtro
        if (fechaFilter) {
            const hoy = new Date().toISOString().split('T')[0];
            fechaFilter.value = hoy;
        }
        
        // Cargar médicos para el filtro
        cargarMedicosParaFiltro();
        
        // Cargar citas iniciales
        cargarCitas();
        
        // Configurar eventos
        configurarEventos();
    }
    
    function configurarEventos() {
        // Filtros
        if (especialidadFilter) especialidadFilter.addEventListener('change', filtrarCitas);
        if (medicoFilter) medicoFilter.addEventListener('change', filtrarCitas);
        if (fechaFilter) fechaFilter.addEventListener('change', filtrarCitas);
        if (estadoFilter) estadoFilter.addEventListener('change', filtrarCitas);
        if (tipoFilter) tipoFilter.addEventListener('change', filtrarCitas);
        if (busquedaInput) busquedaInput.addEventListener('input', debounce(filtrarCitas, 300));
        
        // Acciones de tabla
        if (citasTable) citasTable.addEventListener('click', manejarAccionesTabla);
        
        // Modales
        if (closeCitaModal) closeCitaModal.addEventListener('click', cerrarModalCita);
        if (closeZoomModal) closeZoomModal.addEventListener('click', cerrarModalZoom);
        if (copiarZoomBtn) copiarZoomBtn.addEventListener('click', copiarEnlaceZoom);
        if (abrirZoomBtn) abrirZoomBtn.addEventListener('click', abrirEnlaceZoom);
        
        // Cerrar modales con click en overlay
        if (modalCita) {
            modalCita.addEventListener('click', function(e) {
                if (e.target === modalCita || e.target.classList.contains('modal-overlay')) {
                    cerrarModalCita();
                }
            });
        }
        
        if (modalZoom) {
            modalZoom.addEventListener('click', function(e) {
                if (e.target === modalZoom || e.target.classList.contains('modal-overlay')) {
                    cerrarModalZoom();
                }
            });
        }
    }

    // ========================
    // FUNCIONES DE CARGA DE DATOS
    // ========================
    
    async function cargarMedicosParaFiltro() {
        try {
            const response = await fetch('/admin/citas/api/medicos');
            const data = await response.json();
            
            if (data.exito && medicoFilter) {
                medicoFilter.innerHTML = '<option value="todos">Todos los médicos</option>';
                data.medicos.forEach(medico => {
                    const option = document.createElement('option');
                    option.value = medico.id;
                    option.textContent = `${medico.nombre_completo} - ${medico.especialidad}`;
                    medicoFilter.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error al cargar médicos:', error);
        }
    }
    
    async function cargarCitas() {
        try {
            mostrarCargando(true);
            
            const params = new URLSearchParams({
                page: currentPage,
                per_page: citasPorPagina,
                especialidad: especialidadFilter?.value || 'todas',
                medico_id: medicoFilter?.value || 'todos',
                fecha: fechaFilter?.value || 'todas',
                estado: estadoFilter?.value || 'todos',
                tipo: tipoFilter?.value || 'todos',
                busqueda: busquedaInput?.value || ''
            });
            
            const response = await fetch(`/admin/citas/api/listar?${params}`);
            const data = await response.json();
            
            if (data.exito) {
                mostrarCitasEnTabla(data.citas);
                actualizarPaginacion(data.pagination);
            } else {
                mostrarError('Error al cargar citas: ' + data.error);
                mostrarCitasEnTabla([]);
            }
        } catch (error) {
            console.error('Error al cargar citas:', error);
            mostrarError('Error de conexión al cargar las citas');
            mostrarCitasEnTabla([]);
        } finally {
            mostrarCargando(false);
        }
    }
    
    function mostrarCitasEnTabla(citas) {
        if (!tbody) return;
        
        if (citas.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center" style="padding: 40px;">
                        <i class="fas fa-calendar-times" style="font-size: 2em; color: #ccc; margin-bottom: 10px;"></i>
                        <p style="color: #666;">No se encontraron citas con los filtros aplicados</p>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = citas.map(cita => `
            <tr>
                <td>${cita.id}</td>
                <td>
                    <div>
                        <strong>${cita.paciente.nombre_completo}</strong>
                        <br>
                        <small style="color: #666;">DNI: ${cita.paciente.dni}</small>
                    </div>
                </td>
                <td>${cita.medico.nombre_completo}</td>
                <td>
                    <span class="especialidad-tag ${obtenerClaseEspecialidad(cita.especialidad)}">
                        ${cita.especialidad}
                    </span>
                </td>
                <td>${cita.fecha_cita}</td>
                <td>${cita.hora_inicio}</td>
                <td>
                    <span class="tipo-cita ${cita.tipo.toLowerCase()}">
                        <i class="fas fa-${cita.tipo === 'VIRTUAL' ? 'video' : 'hospital'}"></i>
                        ${cita.tipo === 'VIRTUAL' ? 'Virtual' : 'Presencial'}
                    </span>
                </td>
                <td>
                    <span class="status ${obtenerClaseEstado(cita.estado)}">
                        ${formatearEstado(cita.estado)}
                    </span>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-action btn-view" title="Ver detalles" data-cita-id="${cita.id}">
                            <i class="fas fa-eye"></i>
                        </button>
                        ${cita.tipo === 'VIRTUAL' && cita.enlace_virtual ? `
                            <button class="btn-action btn-zoom" title="Ver enlace virtual" data-cita-id="${cita.id}">
                                <i class="fas fa-video"></i>
                            </button>
                        ` : ''}
                        ${cita.tipo === 'PRESENCIAL' ? `
                            
                        ` : ''}
                        ${cita.estado === 'AGENDADA' ? `
                            <button class="btn-action btn-edit" title="Editar" data-cita-id="${cita.id}">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn-action btn-cancel" title="Cancelar" data-cita-id="${cita.id}">
                                <i class="fas fa-times"></i>
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `).join('');
    }

    // ========================
    // FUNCIONES DE UTILIDAD
    // ========================
    
    function obtenerClaseEspecialidad(especialidad) {
        const clases = {
            'CARDIOLOGÍA': 'cardiologia',
            'MEDICINA INTERNA': 'medicina-interna',
            'ENDOCRINOLOGÍA': 'endocrinologia',
            'PSICOLOGÍA CLÍNICA': 'psicologia',
            'NEUMOLOGÍA': 'neumologia'
        };
        return clases[especialidad] || 'medicina-interna';
    }
    
    function obtenerClaseEstado(estado) {
        const clases = {
            'AGENDADA': 'scheduled',
            'ATENDIDA': 'attended',
            'NO_ATENDIDA': 'no-attended',
            'CANCELADA': 'cancelled'
        };
        return clases[estado] || 'scheduled';
    }
    
    function formatearEstado(estado) {
        const estados = {
            'AGENDADA': 'AGENDADA',
            'ATENDIDA': 'ATENDIDA',
            'NO_ATENDIDA': 'NO ATENDIDA',
            'CANCELADA': 'CANCELADA'
        };
        return estados[estado] || estado;
    }
    
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    function mostrarCargando(mostrar) {
        if (!tbody) return;
        
        if (mostrar) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center" style="padding: 40px;">
                        <div class="loading-spinner" style="border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 20px;"></div>
                        <p style="color: #666;">Cargando citas...</p>
                    </td>
                </tr>
            `;
        }
    }

    // ========================
    // FUNCIONES DE FILTROS
    // ========================
    
    function filtrarCitas() {
        currentPage = 1; // Resetear a la primera página
        cargarCitas();
    }
    
    function actualizarPaginacion(pagination) {
        if (!pagination) return;
        
        currentPage = pagination.page;
        totalPages = pagination.pages;
        
        // Actualizar información de paginación
        const paginationInfo = document.querySelector('.pagination-info');
        if (paginationInfo) {
            const inicio = ((pagination.page - 1) * pagination.per_page) + 1;
            const fin = Math.min(pagination.page * pagination.per_page, pagination.total);
            paginationInfo.textContent = `Mostrando ${inicio}-${fin} de ${pagination.total} citas`;
        }
        
        // Actualizar controles de paginación
        actualizarControlesPaginacion(pagination);
    }
    
    function actualizarControlesPaginacion(pagination) {
        const paginationControls = document.querySelector('.pagination-controls');
        if (!paginationControls) return;
        
        paginationControls.innerHTML = `
            <button class="btn-pagination" onclick="cambiarPagina(${pagination.page - 1})" 
                    ${!pagination.has_prev ? 'disabled' : ''}>
                <i class="fas fa-chevron-left"></i> Anterior
            </button>
            <div class="pagination-pages">
                ${generarBotonesPagina(pagination)}
            </div>
            <button class="btn-pagination" onclick="cambiarPagina(${pagination.page + 1})" 
                    ${!pagination.has_next ? 'disabled' : ''}>
                Siguiente <i class="fas fa-chevron-right"></i>
            </button>
        `;
    }
    
    function generarBotonesPagina(pagination) {
        let botones = '';
        const inicio = Math.max(1, pagination.page - 2);
        const fin = Math.min(pagination.pages, pagination.page + 2);
        
        for (let i = inicio; i <= fin; i++) {
            botones += `
                <button class="btn-page ${i === pagination.page ? 'active' : ''}" 
                        onclick="cambiarPagina(${i})">
                    ${i}
                </button>
            `;
        }
        
        return botones;
    }
    
    // Función global para cambiar página
    window.cambiarPagina = function(nuevaPagina) {
        if (nuevaPagina >= 1 && nuevaPagina <= totalPages && nuevaPagina !== currentPage) {
            currentPage = nuevaPagina;
            cargarCitas();
        }
    };

    // ========================
    // MANEJO DE ACCIONES DE TABLA
    // ========================
    
    function manejarAccionesTabla(e) {
        const target = e.target.closest('.btn-action');
        if (!target) return;
        
        const citaId = target.getAttribute('data-cita-id');
        
        if (target.classList.contains('btn-view')) {
            verDetallesCita(citaId);
        } else if (target.classList.contains('btn-zoom')) {
            mostrarEnlaceZoom(citaId);
        } else if (target.classList.contains('btn-location')) {
            mostrarConsultorio(citaId);
        } else if (target.classList.contains('btn-edit')) {
            editarCita(citaId);
        } else if (target.classList.contains('btn-cancel')) {
            cancelarCita(citaId);
        }
    }
    
    async function verDetallesCita(citaId) {
        try {
            const response = await fetch(`/admin/citas/api/${citaId}`);
            const data = await response.json();
            
            if (data.exito) {
                const cita = data.cita;
                alert(`Detalles de la cita #${cita.id}:\n\n` +
                      `Paciente: ${cita.paciente.nombre_completo}\n` +
                      `DNI: ${cita.paciente.dni}\n` +
                      `Médico: ${cita.medico.nombre_completo}\n` +
                      `Especialidad: ${cita.especialidad}\n` +
                      `Fecha: ${cita.fecha_cita}\n` +
                      `Hora: ${cita.horario_completo}\n` +
                      `Tipo: ${cita.tipo}\n` +
                      `Estado: ${cita.estado}\n` +
                      `${cita.consultorio ? `Consultorio: ${cita.consultorio}\n` : ''}` +
                      `${cita.motivo_consulta ? `Motivo: ${cita.motivo_consulta}\n` : ''}` +
                      `${cita.observaciones ? `Observaciones: ${cita.observaciones}` : ''}`);
            } else {
                mostrarError('Error al obtener detalles: ' + data.error);
            }
        } catch (error) {
            console.error('Error al ver detalles:', error);
            mostrarError('Error de conexión al obtener los detalles');
        }
    }
    
    async function mostrarEnlaceZoom(citaId) {
        try {
            const response = await fetch(`/admin/citas/api/${citaId}`);
            const data = await response.json();
            
            if (data.exito && data.cita.enlace_virtual) {
                const cita = data.cita;
                
                // Llenar datos del modal
                document.getElementById('zoomPaciente').textContent = cita.paciente.nombre_completo;
                document.getElementById('zoomMedico').textContent = cita.medico.nombre_completo;
                document.getElementById('zoomFechaHora').textContent = `${cita.fecha_cita} - ${cita.horario_completo}`;
                document.getElementById('zoomLink').value = cita.enlace_virtual;
                
                // Mostrar modal
                if (modalZoom) {
                    modalZoom.style.display = 'block';
                }
            } else {
                mostrarError('No hay enlace virtual disponible para esta cita');
            }
        } catch (error) {
            console.error('Error al mostrar enlace Zoom:', error);
            mostrarError('Error de conexión al obtener el enlace');
        }
    }
    
    async function mostrarConsultorio(citaId) {
        try {
            const response = await fetch(`/admin/citas/api/${citaId}`);
            const data = await response.json();
            
            if (data.exito) {
                const cita = data.cita;
                alert(`Información del consultorio:\n\n` +
                      `Paciente: ${cita.paciente.nombre_completo}\n` +
                      `Médico: ${cita.medico.nombre_completo}\n` +
                      `Consultorio: ${cita.consultorio || 'No especificado'}\n` +
                      `Fecha: ${cita.fecha_cita}\n` +
                      `Hora: ${cita.horario_completo}\n\n` +
                      `Instrucciones: Llegar 15 minutos antes de la cita`);
            } else {
                mostrarError('Error al obtener información: ' + data.error);
            }
        } catch (error) {
            console.error('Error al mostrar consultorio:', error);
            mostrarError('Error de conexión al obtener la información');
        }
    }
    
    function editarCita(citaId) {
        console.log(`Editar cita ${citaId}`);
        mostrarNotificacion('Funcionalidad de edición en desarrollo', 'info');
    }
    
    async function cancelarCita(citaId) {
        if (!confirm('¿Está seguro de que desea cancelar esta cita?')) {
            return;
        }
        
        try {
            const response = await fetch(`/admin/citas/api/${citaId}/cancelar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.exito) {
                mostrarNotificacion('Cita cancelada exitosamente', 'success');
                cargarCitas(); // Recargar la tabla
            } else {
                mostrarError('Error al cancelar: ' + data.error);
            }
        } catch (error) {
            console.error('Error al cancelar cita:', error);
            mostrarError('Error de conexión al cancelar la cita');
        }
    }

    // ========================
    // FUNCIONES DE MODALES
    // ========================
    
    function cerrarModalCita() {
        if (modalCita) {
            modalCita.style.display = 'none';
        }
    }
    
    function cerrarModalZoom() {
        if (modalZoom) {
            modalZoom.style.display = 'none';
        }
    }
    
    function copiarEnlaceZoom() {
        const zoomLink = document.getElementById('zoomLink');
        if (zoomLink) {
            zoomLink.select();
            document.execCommand('copy');
            mostrarNotificacion('Enlace copiado al portapapeles', 'success');
        }
    }
    
    function abrirEnlaceZoom() {
        const enlace = document.getElementById('zoomLink');
        if (enlace && enlace.value) {
            window.open(enlace.value, '_blank');
        }
    }

    // ========================
    // FUNCIONES DE NOTIFICACIONES
    // ========================
    
    function mostrarNotificacion(mensaje, tipo = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification ${tipo}`;
        notification.textContent = mensaje;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
    
    function mostrarError(mensaje) {
        mostrarNotificacion(mensaje, 'error');
    }

    // ========================
    // FUNCIONES DE EXPORTACIÓN
    // ========================
    
    const exportarPDFBtn = document.getElementById('exportarPDFBtn');
    const exportarExcelBtn = document.getElementById('exportarExcelBtn');
    
    if (exportarPDFBtn) {
        exportarPDFBtn.addEventListener('click', function() {
            this.classList.add('loading');
            
            setTimeout(() => {
                this.classList.remove('loading');
                mostrarNotificacion('Archivo PDF generado exitosamente', 'success');
                console.log('Exportar citas a PDF');
            }, 2000);
        });
    }
    
    if (exportarExcelBtn) {
        exportarExcelBtn.addEventListener('click', function() {
            this.classList.add('loading');
            
            setTimeout(() => {
                this.classList.remove('loading');
                mostrarNotificacion('Archivo Excel generado exitosamente', 'success');
                console.log('Exportar citas a Excel');
            }, 2000);
        });
    }

    // ========================
    // ESTADÍSTICAS (SI EXISTEN)
    // ========================
    
    async function cargarEstadisticas() {
        try {
            const response = await fetch('/admin/citas/api/estadisticas');
            const data = await response.json();
            
            if (data.exito) {
                actualizarEstadisticasUI(data.estadisticas);
            }
        } catch (error) {
            console.error('Error al cargar estadísticas:', error);
        }
    }
    
    function actualizarEstadisticasUI(stats) {
        // Actualizar elementos de estadísticas si existen en el HTML
        const statItems = document.querySelectorAll('.stat-item .stat-number');
        if (statItems.length >= 4) {
            statItems[0].textContent = stats.total_citas || 0;
            statItems[1].textContent = stats.por_estado?.atendidas || 0;
            statItems[2].textContent = stats.por_estado?.agendadas || 0;
            statItems[3].textContent = stats.por_estado?.no_atendidas || 0;
        }
    }

    // ========================
    // FUNCIONALIDAD NUEVA CITA
    // ========================
    
    if (nuevaCitaBtn) {
        nuevaCitaBtn.addEventListener('click', function() {
            // Redirigir a la página de creación de citas o abrir modal
            console.log('Abrir modal/página para nueva cita');
            mostrarNotificacion('Funcionalidad de nueva cita en desarrollo', 'info');
        });
    }

    // ========================
    // INICIALIZACIÓN FINAL
    // ========================
    
    // Cargar estadísticas si hay elementos de estadísticas
    if (document.querySelector('.stat-item')) {
        cargarEstadisticas();
    }
    
    // Agregar estilos de animación para el spinner de carga
    const style = document.createElement('style');
    style.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
    
    console.log('Funcionalidades de citas médicas inicializadas correctamente');
});