// static/js/desktop/admin-dashboard.js

// -----------------------------------------------------------------------------
// FUNCIÓN: cambiar_color
// Propósito: Aplicar estilos visuales a elementos de estado según su valor
// Comportamiento:
//   - Selecciona todos los elementos con clase 'estado'
//   - Añade clase base 'status' para estilos comunes
//   - Clasifica estados como 'active' o 'inactive' según su contenido textual
//   - Se ejecuta al cargar la página (evento DOMContentLoaded)
// -----------------------------------------------------------------------------
function cambiar_color() {
    // Selecciona todos los elementos que muestran estados
    var estados = document.querySelectorAll(".estado");
    
    estados.forEach(function(estado) {
        // Añade clase base para estilos comunes
        estado.classList.add("status");
        
        // Normaliza texto para comparación (mayúsculas sin espacios)
        var texto = estado.innerText.trim().toUpperCase();
        
        // Asigna clase específica según estado
        if (texto === "ACTIVO") {
            estado.classList.add("active");  // Estilo para estado positivo
        } else if (texto === "INACTIVO") {
            estado.classList.add("inactive"); // Estilo para estado negativo
        }
    });
}

// -----------------------------------------------------------------------------
// EVENTO: Inicialización al cargar la página
// Propósito: Ejecutar funciones de configuración inicial
// Notas:
//   - Garantiza que el DOM esté completamente cargado antes de manipularlo
//   - Solo incluye funciones necesarias para el dashboard
// -----------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", function() {
    cambiar_color();  // Aplica estilizado de estados
    
    // NOTA: Aquí se pueden añadir más funciones de inicialización
    // ejemplo: cargarDatosDashboard(), configurarEventListeners()
});