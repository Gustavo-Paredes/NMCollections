document.addEventListener('DOMContentLoaded', function() {
    // Header scroll color - verificar que el elemento existe
    const header = document.getElementById('Header');
    if (header) {
        let ticking = false;
        function updateHeader() {
            const scroll = window.scrollY;
            if (scroll > 50) {
                header.style.backgroundColor = '#222';
            } else {
                header.style.backgroundColor = 'transparent';
            }
            ticking = false;
        }
        
        window.addEventListener('scroll', function() {
            if (!ticking) {
                requestAnimationFrame(updateHeader);
                ticking = true;
            }
        });
    }

    // Carrusel - solo si existe
    const carouselElement = document.querySelector("#carouselNM");
    if (carouselElement && typeof bootstrap !== 'undefined') {
        try {
            const carousel = new bootstrap.Carousel(carouselElement, {
                interval: 4000,
                ride: "carousel",
                pause: false
            });
            carouselElement.addEventListener("mouseenter", () => carousel.pause());
            carouselElement.addEventListener("mouseleave", () => carousel.cycle());
        } catch (error) {
            console.warn('Error inicializando carrusel:', error);
        }
    }

    // Login/Register panels - solo si existen todos los elementos
    const loginPanel = document.getElementById('loginPanel');
    const registerPanel = document.getElementById('registerPanel');
    const showRegister = document.getElementById('showRegister');
    const showLogin = document.getElementById('showLogin');
    
    if (showRegister && showLogin && loginPanel && registerPanel) {
        showRegister.addEventListener('click', function(e) {
            e.preventDefault();
            loginPanel.classList.remove('active');
            registerPanel.classList.add('active');
        });
        
        showLogin.addEventListener('click', function(e) {
            e.preventDefault();
            registerPanel.classList.remove('active');
            loginPanel.classList.add('active');
        });
    }

    // Dropdown menu - Mejorado para manejar clicks y hover
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        
        if (toggle) {
            // Toggle al hacer click
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Cerrar otros dropdowns
                dropdowns.forEach(other => {
                    if (other !== dropdown) {
                        other.classList.remove('active');
                    }
                });
                
                // Toggle del dropdown actual
                dropdown.classList.toggle('active');
            });
        }
    });
    
    // Cerrar dropdown al hacer click fuera
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            dropdowns.forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        }
    });

    // Subastas: contador regresivo
    function actualizarContadoresSubastas() {
        document.querySelectorAll('.subasta-contador').forEach(function(el) {
            const fechaFin = new Date(el.getAttribute('data-fecha-fin'));
            const ahora = new Date();
            let diff = fechaFin - ahora;
            if (diff <= 0) {
                el.textContent = 'Finalizada';
                return;
            }
            const dias = Math.floor(diff / (1000*60*60*24));
            diff -= dias * (1000*60*60*24);
            const horas = Math.floor(diff / (1000*60*60));
            diff -= horas * (1000*60*60);
            const minutos = Math.floor(diff / (1000*60));
            diff -= minutos * (1000*60);
            const segundos = Math.floor(diff / 1000);
            let texto = '';
            if (dias > 0) texto += dias + 'd ';
            texto += (horas < 10 ? '0' : '') + horas + ':';
            texto += (minutos < 10 ? '0' : '') + minutos + ':';
            texto += (segundos < 10 ? '0' : '') + segundos;
            el.textContent = texto;
        });
    }
    if (document.querySelector('.subasta-contador')) {
        setInterval(actualizarContadoresSubastas, 1000);
        actualizarContadoresSubastas();
    }

    // Subastas: ocultar tarjetas si pasó una semana desde el fin
    function ocultarSubastasAntiguas() {
        document.querySelectorAll('.subasta-card').forEach(function(card) {
            const contador = card.querySelector('.subasta-contador');
            if (!contador) return;
            const fechaFinStr = contador.getAttribute('data-fecha-fin');
            if (!fechaFinStr) return;
            const fechaFin = new Date(fechaFinStr);
            const ahora = new Date();
            const diffMs = ahora - fechaFin;
            const unaSemanaMs = 7 * 24 * 60 * 60 * 1000;
            if (diffMs > unaSemanaMs) {
                card.style.display = 'none';
            }
        });
    }
    ocultarSubastasAntiguas();
    setInterval(ocultarSubastasAntiguas, 60 * 60 * 1000); // Revisa cada hora
});

// Función global para toggle de contraseña
function togglePassword(inputId, btn) {
    const input = document.getElementById(inputId);
    const icon = btn.querySelector('i');
    if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    } else {
        input.type = "password";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    }
}



