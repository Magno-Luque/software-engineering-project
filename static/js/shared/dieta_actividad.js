document.addEventListener('DOMContentLoaded', function() {
    // Navegación entre formularios
    const dietForm = document.getElementById('dietForm');
    const activityForm = document.getElementById('activityForm');
    const btnNextDiet = document.getElementById('btnNextDiet');
    const btnBackActivity = document.getElementById('btnBackActivity');
    
    btnNextDiet.addEventListener('click', function() {
        if (dietForm.checkValidity()) {
            dietForm.style.display = 'none';
            activityForm.style.display = 'block';
        } else {
            dietForm.reportValidity();
        }
    });
    
    btnBackActivity.addEventListener('click', function() {
        activityForm.style.display = 'none';
        dietForm.style.display = 'block';
    });
    
    // Manejar envío del formulario completo
    activityForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (activityForm.checkValidity()) {
            const formData = new FormData(dietForm);
            const activityData = new FormData(activityForm);
            
            for (let [key, value] of activityData.entries()) {
                formData.append(key, value);
            }
            
            // Crear el modal de confirmación mejorado
            const confirmationModal = document.createElement('div');
            confirmationModal.className = 'confirmation-modal';
            confirmationModal.innerHTML = `
                <div class="confirmation-content">
                    <div class="confirmation-header">
                        <i class="fas fa-check-circle"></i>
                        <h3>¡Registro guardado con éxito!</h3>
                    </div>
                    
                    <div class="confirmation-body">
                        <p>Tus datos de dieta y actividad física han sido registrados correctamente.</p>
                        <!-- Sección de Dieta -->
                        <div class="confirmation-section">
                            <h4><i class="fas fa-utensils"></i> Resumen de Dieta</h4>
                            
                            <!-- Desayuno -->
                            <div class="meal-confirmation">
                                <h5><i class="fas fa-sun"></i> Desayuno</h5>
                                <div class="confirmation-row">
                                    <span class="confirmation-label">Comida:</span>
                                    <span class="confirmation-value">${document.getElementById('desayuno_comida').value || 'No especificado'}</span>
                                </div>
                                <div class="confirmation-row">
                                    <span class="confirmation-label">Porción:</span>
                                    <span class="confirmation-value">${document.getElementById('desayuno_porcion').value || 'No especificado'}</span>
                                </div>
                                ${document.getElementById('desayuno_notas').value ? `
                                <div class="confirmation-row">
                                    <span class="confirmation-label">Notas:</span>
                                    <span class="confirmation-value">${document.getElementById('desayuno_notas').value}</span>
                                </div>
                                ` : ''}
                            </div>
                            
                            <!-- Almuerzo -->
                            <div class="meal-confirmation">
                                <h5><i class="fas fa-utensils"></i> Almuerzo</h5>
                                <div class="confirmation-row">
                                    <span class="confirmation-label">Comida:</span>
                                    <span class="confirmation-value">${document.getElementById('almuerzo_comida').value || 'No especificado'}</span>
                                </div>
                                <div class="confirmation-row">
                                    <span class="confirmation-label">Porción:</span>
                                    <span class="confirmation-value">${document.getElementById('almuerzo_porcion').value || 'No especificado'}</span>
                                </div>
                                ${document.getElementById('almuerzo_notas').value ? `
                                <div class="confirmation-row">
                                    <span class="confirmation-label">Notas:</span>
                                    <span class="confirmation-value">${document.getElementById('almuerzo_notas').value}</span>
                                </div>
                                ` : ''}
                            </div>
                            
                            <!-- Cena -->
                            <div class="meal-confirmation">
                                <h5><i class="fas fa-moon"></i> Cena</h5>
                                <div class="confirmation-row">
                                    <span class="confirmation-label">Comida:</span>
                                    <span class="confirmation-value">${document.getElementById('cena_comida').value || 'No especificado'}</span>
                                </div>
                                <div class="confirmation-row">
                                    <span class="confirmation-label">Porción:</span>
                                    <span class="confirmation-value">${document.getElementById('cena_porcion').value || 'No especificado'}</span>
                                </div>
                                ${document.getElementById('cena_notas').value ? `
                                <div class="confirmation-row">
                                    <span class="confirmation-label">Notas:</span>
                                    <span class="confirmation-value">${document.getElementById('cena_notas').value}</span>
                                </div>
                                ` : ''}
                            </div>
                        </div>
                        
                        <!-- Sección de Actividad Física -->
                        <div class="confirmation-section">
                            <h4><i class="fas fa-running"></i> Actividad Física</h4>
                            <div class="confirmation-row">
                                <span class="confirmation-label">Tipo:</span>
                                <span class="confirmation-value">${document.getElementById('tipo_actividad').value || 'No especificado'}</span>
                            </div>
                            <div class="confirmation-row">
                                <span class="confirmation-label">Intensidad:</span>
                                <span class="confirmation-value">${document.getElementById('intensidad').value || 'No especificado'}</span>
                            </div>
                            <div class="confirmation-row">
                                <span class="confirmation-label">Duración:</span>
                                <span class="confirmation-value">${document.getElementById('tiempo').value || '0'} minutos</span>
                            </div>
                            ${document.getElementById('notas_actividad').value ? `
                            <div class="confirmation-row">
                                <span class="confirmation-label">Notas:</span>
                                <span class="confirmation-value">${document.getElementById('notas_actividad').value}</span>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                    
                    <div class="confirmation-actions">
                        <button class="btn btn-primary" id="confirmClose">Aceptar</button>
                    </div>
                </div>
            `;
            
            // Estilos mejorados para el modal
            const style = document.createElement('style');
            style.textContent = `
                .confirmation-modal {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background-color: rgba(0,0,0,0.5);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    z-index: 1000;
                    opacity: 0;
                    animation: fadeIn 0.3s forwards;
                }
                
                @keyframes fadeIn {
                    to { opacity: 1; }
                }
                
                .confirmation-content {
                    background-color: var(--card-bg);
                    border-radius: 10px;
                    width: 90%;
                    max-width: 600px;
                    max-height: 80vh;
                    overflow-y: auto;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                    transform: translateY(-20px);
                    animation: slideUp 0.3s forwards;
                }
                
                @keyframes slideUp {
                    to { transform: translateY(0); }
                }
                
                .confirmation-header {
                background-color: var(--secondary-blue);
                color: var(--text-light);
                padding: 20px;
                text-align: center;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
                
                .confirmation-header i {
                    font-size: 3rem;
                    margin-bottom: 10px;
                }
                
                .confirmation-header h3 {
                    margin: 0 0 5px 0;
                    font-size: 1.5rem;
                }
                
                .confirmation-header p {
                    margin: 0;
                    opacity: 0.9;
                    font-size: 0.9rem;
                }
                
                .confirmation-body {
                    padding: 20px;
                    text-align: center;
                }

                .confirmation-body p {
                    color: var(--text-dark);
                    margin-bottom: 20px;
                    text-align: center;
                }
                
                .confirmation-section {
                    background-color: var(--light-blue);
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 15px;
                }
                
                .confirmation-section h4 {
                    color: var(--secondary-blue);
                    margin-top: 0;
                    margin-bottom: 15px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                
                .meal-confirmation {
                    background-color: rgba(255,255,255,0.7);
                    border-radius: 6px;
                    padding: 12px;
                    margin-bottom: 12px;
                }
                
                .meal-confirmation h5 {
                    color: var(--primary-blue);
                    margin-top: 0;
                    margin-bottom: 10px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    font-size: 0.95rem;
                }
                
                .confirmation-row {
                    display: flex;
                    padding: 6px 0;
                    font-size: 0.9rem;
                }
                
                .confirmation-row.full-width {
                    display: flex;
                    justify-content: space-between;
                    background: none;
                    padding: 10px 0 0 0;
                    border-top: 1px dashed var(--border-color);
                    margin-top: 10px;
                }
                
                .confirmation-label {
                    font-weight: bold;
                    color: var(--text-dark);
                    min-width: 80px;
                    margin-right: 10px;
                }
                
                .confirmation-value {
                    color: var(--text-gray);
                    flex-grow: 1;
                    word-break: break-word;
                }
                
                .confirmation-actions {
                    padding: 15px 20px;
                    display: flex;
                    justify-content: center;
                    border-top: 1px solid var(--border-color);
                }
                
                @media (max-width: 480px) {
                    .confirmation-row {
                        flex-direction: column;
                        gap: 2px;
                    }
                    
                    .confirmation-label {
                        min-width: auto;
                    }
                }
            `;
            
            document.head.appendChild(style);
            document.body.appendChild(confirmationModal);
            
            document.getElementById('confirmClose').addEventListener('click', function() {
                document.body.removeChild(confirmationModal);
                document.head.removeChild(style);
                
                fetch(dietForm.action, {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (response.ok) {
                        dietForm.reset();
                        activityForm.reset();
                        activityForm.style.display = 'none';
                        dietForm.style.display = 'block';
                    } else {
                        throw new Error('Error al guardar los datos');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Hubo un error al guardar los datos. Por favor, inténtalo de nuevo.');
                });
            });
        } else {
            activityForm.reportValidity();
        }
    });
});