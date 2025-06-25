// static/js/shared/main.js
document.addEventListener('DOMContentLoaded', () => {
    console.log('MiControl app cargada.');

    // Funcionalidad básica del menú toggle (si se implementa colapso del sidebar)
    const menuToggle = document.querySelector('.menu-toggle-icon');
    const sidebar = document.querySelector('.sidebar');
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => { 
            sidebar.classList.toggle('collapsed');
            // Aquí se podría ajustar el layout del main-content si el sidebar se colapsa
        });
    }

    // Lógica para resaltar el enlace activo en el sidebar
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.sidebar-nav ul li a');

    sidebarLinks.forEach(link => {
        // Para el dashboard, "/" también debe considerarse activo
        if (link.getAttribute('href') === currentPath || (link.getAttribute('href') === '/' && currentPath === '/admin/dashboard')) {
            link.closest('li').classList.add('active');
        } else {
            link.closest('li').classList.remove('active');
        }
    });
});