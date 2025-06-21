document.addEventListener('DOMContentLoaded', function() {
    // Limpiar formulario
    document.getElementById('btnLimpiar').addEventListener('click', function() {
        document.getElementById('biometricForm').reset();
    });
    
    // Validación de presión arterial
    document.getElementById('presion_sistolica').addEventListener('change', function() {
        if (parseInt(this.value) < parseInt(document.getElementById('presion_diastolica').value)) {
            alert('La presión sistólica debe ser mayor que la diastólica');
            this.value = '';
        }
    });
    
    document.getElementById('presion_diastolica').addEventListener('change', function() {
        if (parseInt(this.value) > parseInt(document.getElementById('presion_sistolica').value)) {
            alert('La presión diastólica debe ser menor que la sistólica');
            this.value = '';
        }
    });

    // Agregar esto dentro del eventListener DOMContentLoaded, después de tus validaciones
    document.getElementById('biometricForm').addEventListener('submit', function(e) {
        e.preventDefault(); // Prevenir envío normal para mostrar el mensaje primero
        
        // Crear el modal de confirmación
        const confirmationModal = document.createElement('div');
        confirmationModal.className = 'confirmation-modal';
        confirmationModal.innerHTML = `
            <div class="confirmation-content">
                <div class="confirmation-header">
                    <i class="fas fa-check-circle"></i>
                    <h3>¡Registro guardado con éxito!</h3>
                </div>
                <div class="confirmation-body">
                    <p>Tus datos biométricos han sido registrados correctamente.</p>
                    <div class="confirmation-values">
                        <div class="confirmation-item">
                            <span class="confirmation-label">Glucosa:</span>
                            <span class="confirmation-value">${document.getElementById('glucosa').value} mg/dL</span>
                        </div>
                        <div class="confirmation-item">
                            <span class="confirmation-label">Presión Arterial:</span>
                            <span class="confirmation-value">${document.getElementById('presion_sistolica').value}/${document.getElementById('presion_diastolica').value} mmHg</span>
                        </div>
                        <div class="confirmation-item">
                            <span class="confirmation-label">Frecuencia Cardíaca:</span>
                            <span class="confirmation-value">${document.getElementById('frecuencia_cardiaca').value} lpm</span>
                        </div>
                    </div>
                </div>
                <div class="confirmation-actions">
                    <button class="btn btn-primary" id="confirmClose">Aceptar</button>
                </div>
            </div>
        `;
        
        // Estilos para el modal (podrías mover esto a tu CSS)
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
                max-width: 500px;
                overflow: hidden;
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
                margin: 0;
                font-size: 1.5rem;
            }
            
            .confirmation-body {
                padding: 20px;
                text-align: center;
            }
            
            .confirmation-body p {
                color: var(--text-dark);
                margin-bottom: 20px;
            }
            
            .confirmation-values {
                background-color: var(--light-blue);
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
            }
            
            .confirmation-item {
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px dashed var(--border-color);
            }
            
            .confirmation-item:last-child {
                border-bottom: none;
            }
            
            .confirmation-label {
                display: block;
                margin-bottom: 8px;
                font-weight: bold;
                font-family: Arial, sans-serif;
                color: var(--text-dark);
                text-align: left;
            }
            
            .confirmation-value {
                color: var(--secondary-blue);
                font-weight: bold;
            }
            
            .confirmation-actions {
                padding: 15px 20px;
                display: flex;
                justify-content: center;
                border-top: 1px solid var(--border-color);
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(confirmationModal);
        
        // Cerrar el modal y enviar el formulario
        document.getElementById('confirmClose').addEventListener('click', function() {
            // Primero quitamos el modal
            document.body.removeChild(confirmationModal);
            document.head.removeChild(style);
            
            // Luego enviamos el formulario realmente
            document.getElementById('biometricForm').submit();
        });
    });
});