// =========================================================================
// ANIMACIONES GLOBALES DEL SISTEMA (ANIME.JS)
// =========================================================================

// Animación de Papelera y Arrugado de Papel
window.animarLimpieza = function(callback) {
    const overlay = document.getElementById('trash-overlay');
    if(!overlay || !window.anime) {
        callback();
        return;
    }
    
    // Crear el "Papel" con un diseño más realista (con la esquina doblada)
    const paper = document.createElement('div');
    paper.innerHTML = `<svg width="80" height="100" viewBox="0 0 60 80">
        <path d="M 5 5 L 40 5 L 55 20 L 55 75 L 5 75 Z" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/>
        <path d="M 40 5 L 40 20 L 55 20" fill="none" stroke="#94a3b8" stroke-width="2"/>
        <line x1="15" y1="35" x2="45" y2="35" stroke="#cbd5e1" stroke-width="4" stroke-linecap="round"/>
        <line x1="15" y1="50" x2="45" y2="50" stroke="#cbd5e1" stroke-width="4" stroke-linecap="round"/>
        <line x1="15" y1="65" x2="35" y2="65" stroke="#cbd5e1" stroke-width="4" stroke-linecap="round"/>
    </svg>`;
    paper.style.position = 'absolute';
    // Comienza en el centro de la pantalla
    paper.style.top = '50%';
    paper.style.left = '50%';
    paper.style.transform = 'translate(-50%, -50%)';
    paper.style.zIndex = '10001';
    
    // Crear la "Papelera" (Con tapa separada para animarla)
    const trash = document.createElement('div');
    trash.innerHTML = `<svg width="120" height="140" viewBox="0 0 100 120" style="filter: drop-shadow(0 0 15px rgba(239,68,68,0.3));">
        <!-- Tapa de la papelera -->
        <g class="trash-lid" style="transform-origin: 20px 30px;">
            <rect x="15" y="25" width="70" height="8" rx="4" fill="#ef4444" />
            <rect x="40" y="15" width="20" height="10" rx="3" fill="#ef4444" />
        </g>
        <!-- Cuerpo de la papelera -->
        <path d="M 22 35 L 78 35 L 70 110 L 30 110 Z" fill="#ef4444" />
        <line x1="40" y1="45" x2="40" y2="100" stroke="#b91c1c" stroke-width="4" stroke-linecap="round"/>
        <line x1="60" y1="45" x2="60" y2="100" stroke="#b91c1c" stroke-width="4" stroke-linecap="round"/>
    </svg>`;
    trash.style.position = 'absolute';
    // Ubicar la papelera en la parte SUPERIOR de la pantalla
    trash.style.top = '15%';
    trash.style.left = '50%';
    trash.style.transform = 'translate(-50%, -50%)';
    trash.style.zIndex = '10000';
    trash.style.opacity = '0';
    
    overlay.appendChild(trash);
    overlay.appendChild(paper);
    
    // Línea de tiempo de la animación
    const tl = anime.timeline({
        easing: 'easeOutExpo'
    });
    
    // 1. Aparece la papelera en la parte superior
    tl.add({
        targets: trash,
        opacity: [0, 1],
        translateY: [-50, 0],
        duration: 400
    })
    // 2. Efecto de "Arrugar" el papel (se comprime el SVG simulando deformación 3D)
    .add({
        targets: paper,
        scaleX: [1, 0.4],
        scaleY: [1, 0.5],
        rotate: '3turn',
        duration: 800,
        easing: 'easeInOutElastic(1, .6)'
    }, '-=200')
    // 3. La tapa de la papelera se ABRE
    .add({
        targets: '.trash-lid',
        rotate: '-50deg',
        duration: 300,
        easing: 'easeOutQuad'
    })
    // 4. El papel arrugado VUELA hacia arriba, entrando a la papelera
    .add({
        targets: paper,
        top: '15%',
        scaleX: 0,
        scaleY: 0,
        opacity: [1, 0],
        duration: 500,
        easing: 'easeInBack'
    }, '-=100')
    // 5. La tapa se CIERRA y la papelera tiembla por el impacto
    .add({
        targets: '.trash-lid',
        rotate: '0deg',
        duration: 200,
        easing: 'easeInQuad'
    })
    .add({
        targets: trash,
        rotate: [0, -10, 10, -10, 10, 0],
        scale: [1, 1.1, 1],
        duration: 400
    }, '-=200')
    // 6. La papelera desaparece
    .add({
        targets: trash,
        opacity: [1, 0],
        translateY: [0, -50],
        duration: 400,
        complete: () => {
            overlay.innerHTML = '';
            callback(); // Llama a la lógica de limpieza de inputs
        }
    });
};

// =========================================================================
// TRANSICIÓN DE PÁGINAS (Interceptando enlaces)
// =========================================================================
document.addEventListener('DOMContentLoaded', () => {
    // Animación de Entrada al cargar cualquier HTML
    anime({
        targets: '.page-transition-wrapper',
        opacity: [0, 1],
        translateY: [20, 0],
        duration: 600,
        easing: 'easeOutExpo'
    });

    // Animación de Salida al hacer click en los enlaces del navbar
    const pageLinks = document.querySelectorAll('.page-link, a[href^="/"]');
    pageLinks.forEach(link => {
        if(link.getAttribute('href').startsWith('#') || link.getAttribute('target') === '_blank') return;

        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetUrl = link.href;

            anime({
                targets: '.page-transition-wrapper',
                opacity: [1, 0],
                translateY: [0, -20],
                duration: 400,
                easing: 'easeInQuad',
                complete: () => {
                    window.location.href = targetUrl;
                }
            });
        });
    });

    // =========================================================================
    // ANIMACIONES DE ENTRADA ESCALONADA (STAGGERED)
    // =========================================================================
    
    // 1. Escalonar las tarjetas de los módulos si existen
    if (document.querySelector('.module-card')) {
        anime({
            targets: '.module-card',
            translateY: [30, 0],
            opacity: [0, 1],
            delay: anime.stagger(100, {start: 300}),
            duration: 800,
            easing: 'easeOutElastic(1, .8)'
        });
    }

    // 2. Escalonar los inputs del formulario
    if (document.querySelector('.input-group')) {
        anime({
            targets: '.input-group',
            translateX: [-20, 0],
            opacity: [0, 1],
            delay: anime.stagger(80, {start: 400}),
            duration: 600,
            easing: 'easeOutExpo'
        });
    }

    // 3. Escalonar las filas de la tabla cuando se generan
    // Creamos una función global que se pueda llamar desde main.js después de renderizar resultados
    window.animarTabla = function(selector) {
        const rows = document.querySelectorAll(`${selector} tbody tr`);
        if (rows.length > 0) {
            anime({
                targets: rows,
                opacity: [0, 1],
                translateX: [10, 0],
                delay: anime.stagger(30),
                duration: 400,
                easing: 'easeOutQuad'
            });
        }
    };

    // =========================================================================
    // MODO OSCURO / MODO CLARO (Toggle con Anime.js)
    // =========================================================================
    const themeBtn = document.getElementById('theme-btn');
    const themeIcon = document.getElementById('theme-icon');
    
    if (themeBtn && themeIcon) {
        // Inicializar icono según el tema actual guardado
        if (document.documentElement.classList.contains('light')) {
            themeIcon.classList.remove('ph-moon');
            themeIcon.classList.add('ph-sun');
        }
        
        themeBtn.addEventListener('click', () => {
            const htmlEl = document.documentElement;
            const isDark = htmlEl.classList.contains('dark');
            
            // 1. Ocultar el icono actual girando
            anime({
                targets: themeIcon,
                rotate: '1turn',
                scale: 0,
                duration: 300,
                easing: 'easeInBack',
                complete: () => {
                    // Cambiar el tema y el icono
                    if (isDark) {
                        htmlEl.classList.remove('dark');
                        htmlEl.classList.add('light');
                        themeIcon.classList.remove('ph-moon');
                        themeIcon.classList.add('ph-sun');
                        localStorage.setItem('theme', 'light');
                    } else {
                        htmlEl.classList.remove('light');
                        htmlEl.classList.add('dark');
                        themeIcon.classList.remove('ph-sun');
                        themeIcon.classList.add('ph-moon');
                        localStorage.setItem('theme', 'dark');
                    }
                    
                    // 2. Aparecer el nuevo icono
                    anime({
                        targets: themeIcon,
                        rotate: '0turn',
                        scale: [0, 1],
                        duration: 400,
                        easing: 'easeOutBack'
                    });
                }
            });
        });
    }
});
