// static/js/desktop/desktop-auth.js
const DesktopAuth = {
    config: null,
    
    init(config) {
        this.config = config;
        this.setupEventListeners();
        this.checkSession();
    },
    
    setupEventListeners() {
        const loginForm = document.getElementById('desktopLoginForm');
        const togglePassword = document.getElementById('desktopTogglePassword');
        const forgotLink = document.getElementById('desktopForgotLink');
        
        if (loginForm) {
            loginForm.addEventListener('submit', this.handleLogin.bind(this));
        }
        
        if (togglePassword) {
            togglePassword.addEventListener('click', this.togglePasswordVisibility);
        }
        
        if (forgotLink) {
            forgotLink.addEventListener('click', this.showForgotModal.bind(this));
        }
        
        // Manejar modal de recuperación
        this.setupForgotModal();
    },
    
    async handleLogin(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const usuario = formData.get('usuario');
        const password = formData.get('password');
        
        if (!this.validateForm(usuario, password)) {
            return;
        }
        
        this.showLoading(true);
        
        try {
            const response = await fetch(this.config.apiEndpoints.login, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ usuario, password })
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.handleLoginSuccess(result);
            } else {
                this.handleLoginError(result.message || 'Error de autenticación');
            }
        } catch (error) {
            console.error('Error de conexión:', error);
            this.handleLoginError('Error de conexión. Verifique su conexión a internet.');
        } finally {
            this.showLoading(false);
        }
    },
    
    validateForm(usuario, password) {
        const errors = {};
        
        if (!usuario || !usuario.trim()) {
            errors.usuario = 'El usuario es requerido';
        } else if (usuario.trim().length < 3) {
            errors.usuario = 'El usuario debe tener al menos 3 caracteres';
        }
        
        if (!password || !password.trim()) {
            errors.password = 'La contraseña es requerida';
        } else if (password.length < 6) {
            errors.password = 'La contraseña debe tener al menos 6 caracteres';
        }
        
        this.displayErrors(errors);
        return Object.keys(errors).length === 0;
    },
    
    displayErrors(errors) {
        // Limpiar errores previos
        document.querySelectorAll('.desktop-field-error').forEach(el => {
            el.textContent = '';
            el.style.display = 'none';
        });
        
        // Limpiar clases de error en inputs
        document.querySelectorAll('.desktop-form-input').forEach(input => {
            input.classList.remove('error');
        });
        
        // Mostrar nuevos errores
        Object.keys(errors).forEach(field => {
            const errorEl = document.getElementById(`${field}-error`);
            const inputEl = document.getElementById(`desktop-${field}`);
            
            if (errorEl) {
                errorEl.textContent = errors[field];
                errorEl.style.display = 'block';
            }
            
            if (inputEl) {
                inputEl.classList.add('error');
                inputEl.focus();
            }
        });
    },
    
    handleLoginSuccess(result) {
        this.showAlert('Inicio de sesión exitoso. Redirigiendo...', 'success');
        
        // Redirigir según el rol
        const redirectUrl = this.config.redirectUrls[result.role];
        if (redirectUrl) {
            setTimeout(() => {
                window.location.href = redirectUrl;
            }, 1500);
        } else {
            console.error('No se encontró URL de redirección para el rol:', result.role);
            this.showAlert('Error: Rol no reconocido', 'error');
        }
    },
    
    handleLoginError(message) {
        this.showAlert(message, 'error');
        
        // Limpiar campos de contraseña por seguridad
        const passwordInput = document.getElementById('desktop-password');
        if (passwordInput) {
            passwordInput.value = '';
        }
    },
    
    showAlert(message, type) {
        const alertsContainer = document.getElementById('desktop-auth-alerts');
        const alertClass = type === 'success' ? 'desktop-alert-success' : 'desktop-alert-error';
        
        alertsContainer.innerHTML = `
            <div class="desktop-alert ${alertClass}">
                <div class="alert-content">
                    <span class="alert-message">${message}</span>
                    <button type="button" class="alert-close" onclick="this.parentElement.parentElement.remove()">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
            </div>
        `;
        alertsContainer.style.display = 'block';
        
        // Auto-ocultar después de 8 segundos
        setTimeout(() => {
            if (alertsContainer.firstElementChild) {
                alertsContainer.firstElementChild.remove();
                if (!alertsContainer.children.length) {
                    alertsContainer.style.display = 'none';
                }
            }
        }, 8000);
    },
    
    showLoading(show) {
        const button = document.getElementById('desktopLoginButton');
        const btnText = button.querySelector('.btn-text');
        const btnLoading = button.querySelector('.btn-loading');
        
        if (show) {
            btnText.style.display = 'none';
            btnLoading.style.display = 'flex';
            button.disabled = true;
            button.classList.add('loading');
        } else {
            btnText.style.display = 'block';
            btnLoading.style.display = 'none';
            button.disabled = false;
            button.classList.remove('loading');
        }
    },
    
    togglePasswordVisibility() {
        const passwordInput = document.getElementById('desktop-password');
        const toggleButton = document.getElementById('desktopTogglePassword');
        
        if (passwordInput.getAttribute('type') === 'password') {
            passwordInput.setAttribute('type', 'text');
            toggleButton.setAttribute('aria-label', 'Ocultar contraseña');
        } else {
            passwordInput.setAttribute('type', 'password');
            toggleButton.setAttribute('aria-label', 'Mostrar contraseña');
        }
    },
    
    async checkSession() {
        try {
            const response = await fetch(this.config.apiEndpoints.checkSession);
            if (response.ok) {
                const result = await response.json();
                if (result.authenticated) {
                    const redirectUrl = this.config.redirectUrls[result.role];
                    if (redirectUrl) {
                        window.location.href = redirectUrl;
                    }
                }
            }
        } catch (error) {
            console.log('No hay sesión activa o error al verificar:', error);
        }
    },
    
    showForgotModal() {
        const modal = document.getElementById('desktopForgotModal');
        if (modal) {
            modal.style.display = 'flex';
            // Focus en el input del modal
            const input = modal.querySelector('#forgot-usuario');
            if (input) {
                setTimeout(() => input.focus(), 100);
            }
        }
    },
    
    setupForgotModal() {
        const modal = document.getElementById('desktopForgotModal');
        const closeBtn = document.getElementById('closeDesktopForgotModal');
        const cancelBtn = document.getElementById('cancelDesktopForgot');
        const form = document.getElementById('desktopForgotForm');
        
        // Cerrar modal
        [closeBtn, cancelBtn].forEach(btn => {
            if (btn) {
                btn.addEventListener('click', () => {
                    modal.style.display = 'none';
                });
            }
        });
        
        // Cerrar al hacer click fuera
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        }
        
        // Manejar formulario de recuperación
        if (form) {
            form.addEventListener('submit', this.handleForgotPassword.bind(this));
        }
    },
    
    async handleForgotPassword(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const usuario = formData.get('forgot-usuario');
        
        if (!usuario || !usuario.trim()) {
            this.showAlert('El campo usuario es requerido', 'error');
            return;
        }
        
        try {
            const response = await fetch(this.config.apiEndpoints.forgotPassword, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ usuario: usuario.trim() })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert(result.message, 'success');
                // Cerrar modal después de 2 segundos
                setTimeout(() => {
                    document.getElementById('desktopForgotModal').style.display = 'none';
                }, 2000);
            } else {
                this.showAlert(result.message, 'error');
            }
        } catch (error) {
            this.showAlert('Error de conexión. Intente nuevamente.', 'error');
        }
    }
};