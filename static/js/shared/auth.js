// static/js/shared/auth.js
document.addEventListener('DOMContentLoaded', () => {
    console.log('Módulo de autenticación cargado.');

    const loginForm = document.getElementById('loginForm');

    if (loginForm) {
        loginForm.addEventListener('submit', (event) => {
            // Aquí puedes añadir validaciones básicas del lado del cliente
            const usernameInput = document.getElementById('username');
            const passwordInput = document.getElementById('password');
 
            if (usernameInput.value.trim() === '' || passwordInput.value.trim() === '') {
                alert('Por favor, ingresa tu usuario y contraseña.');
                event.preventDefault(); // Evita que el formulario se envíe si hay campos vacíos
            }
            // La lógica de envío real (petición POST) la maneja Flask en app.py
        });
    }

    // Opcional: Eliminar mensajes flash después de un tiempo
    const flashMessages = document.querySelectorAll('.flash-messages li');
    if (flashMessages.length > 0) {
        setTimeout(() => {
            flashMessages.forEach(msg => msg.remove());
        }, 5000); // Los mensajes desaparecen después de 5 segundos
    }
});