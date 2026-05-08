// Configuración y lógica para el tutorial interactivo usando driver.js
document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('tutorial-btn');
    if (btn) {
        btn.addEventListener('click', iniciarTutorial);
    }
});

function iniciarTutorial() {
    const driver = window.driver.js.driver;
    
    // Obtenemos la ruta actual para dar un tutorial contextual
    const path = window.location.pathname;
    
    let steps = [];
    
    if (path === '/' || path === '/index.html' || path === '') {
        steps = [
            {
                element: '.brand',
                popover: { title: '¡Bienvenido!', description: 'Esta es la Suite Numérica Pro, tu herramienta para resolver problemas matemáticos de manera avanzada. Te daré un rápido tour.', side: "bottom", align: 'start' }
            },
            {
                element: '.nav-menu',
                popover: { title: 'Navegación', description: 'Usa este menú para cambiar entre los diferentes módulos de cálculo: Ecuaciones de 1 variable, Raíces de Polinomios y Sistemas Multivariable.', side: "bottom" }
            },
            {
                element: '#theme-btn',
                popover: { title: 'Modo Visual', description: 'Cambia entre el modo Día y Noche para ajustar la visualización a tus preferencias visuales.', side: "left" }
            },
            {
                element: '.modules-grid',
                popover: { title: 'Módulos Directos', description: 'Selecciona cualquiera de estas tarjetas para comenzar a resolver problemas al instante.', side: "top" }
            }
        ];
    } else if (path.includes('no-lineales')) {
        steps = [
            {
                popover: { title: 'Buscador de Raíces', description: 'Este módulo te permite encontrar raíces reales de una sola ecuación utilizando varios métodos iterativos.' }
            },
            {
                element: '#ecuacion-nl',
                popover: { title: '1. Ingresa la Ecuación', description: 'Escribe tu función f(x) usando notación matemática estándar. Ejemplos: sqrt(x) - cos(x), x**3 + 2*x - 1, o exp(x).', side: "bottom" }
            },
            {
                element: '#metodo-nl',
                popover: { title: '2. Selecciona el Método', description: 'Elige entre Bisección, Regla Falsa, Newton-Raphson, etc. Los campos de entrada se adaptarán automáticamente al método.', side: "bottom" }
            },
            {
                element: '#angulo-nl',
                popover: { title: '3. Radianes o Grados', description: 'Si usas funciones trigonométricas, elige el sistema de ángulos adecuado. Por defecto en matemáticas siempre se usan Radianes.', side: "bottom" }
            },
            {
                element: '#tol-nl',
                popover: { title: '4. Tolerancia (Error)', description: 'Establece el porcentaje de error permitido (ej. 0.01) para que el algoritmo sepa cuándo detenerse.', side: "bottom" }
            },
            {
                element: '#campos-dinamicos-nl',
                popover: { title: '5. Valores Iniciales', description: 'Llena los intervalos o el punto inicial requeridos por el método que seleccionaste.', side: "top" }
            },
            {
                element: '.form-actions',
                popover: { title: '6. Calcular y Limpiar', description: '¡Haz clic en Calcular para procesar tu ecuación! Si necesitas empezar de cero, usa Limpiar.', side: "top" }
            },
            {
                element: '.table-container',
                popover: { title: 'Resultados Detallados', description: 'Aquí aparecerá la tabla paso a paso de todas las iteraciones generadas. Puedes exportarla a Excel con el botón inferior.', side: "top" }
            }
        ];
    } else if (path.includes('polinomios')) {
        steps = [
            {
                popover: { title: 'Raíces de Polinomios', description: 'Calcula raíces reales y complejas de polinomios puros de cualquier grado.' }
            },
            {
                element: '#grado-pol',
                popover: { title: '1. Grado del Polinomio', description: 'Establece el exponente mayor del polinomio. Esto generará los espacios necesarios para los coeficientes.', side: "bottom" }
            },
            {
                element: '#metodo-pol',
                popover: { title: '2. Elige el Algoritmo', description: 'Müller y Bairstow son excelentes para encontrar raíces imaginarias/complejas.', side: "bottom" }
            },
            {
                element: '#container-coefs',
                popover: { title: '3. Coeficientes', description: 'Llena cada coeficiente acompañante de x. Si no existe un término, asegúrate de escribir 0.', side: "top" }
            },
            {
                element: '.form-actions',
                popover: { title: '4. Ejecutar', description: 'Haz clic aquí para resolver. El sistema te mostrará la tabla de evaluación y en la caja inferior la solución estructurada.', side: "top" }
            }
        ];
    } else if (path.includes('sistemas')) {
        steps = [
            {
                popover: { title: 'Sistemas No Lineales', description: 'Resuelve sistemas de múltiples ecuaciones con múltiples variables usando el método analítico de Newton-Raphson Multivariable.' }
            },
            {
                element: '#n-sis',
                popover: { title: '1. Dimensiones del Sistema', description: 'Define cuántas ecuaciones tiene tu sistema (n). Esto adaptará la interfaz para recibir f_1, f_2, etc.', side: "bottom" }
            },
            {
                element: '#container-sis',
                popover: { title: '2. Ecuaciones y Vectores Iniciales', description: 'Escribe cada ecuación igualada a cero (f_i). A la par, define un valor numérico inicial para que la variable correspondiente pueda arrancar.', side: "top" }
            },
            {
                element: '#tol-sis',
                popover: { title: '3. Control de Iteraciones', description: 'Debes definir una Tolerancia y obligatoriamente un límite Máximo de Iteraciones para evitar bucles infinitos si el sistema diverge.', side: "bottom" }
            },
            {
                element: '.form-actions',
                popover: { title: '4. Calcular Jacobiano', description: 'Haz clic aquí. El sistema calculará las derivadas parciales automáticamente, invertirá el Jacobiano y te mostrará el proceso iterativo.', side: "top" }
            }
        ];
    } else {
        steps = [
            {
                popover: { title: 'Información', description: 'Explora los módulos a través del menú superior para encontrar herramientas especializadas.' }
            }
        ];
    }

    const driverObj = driver({
        showProgress: true,
        animate: true,
        popoverClass: 'driverjs-theme', // Para inyectar nuestros propios estilos de paleta
        nextBtnText: 'Siguiente ➔',
        prevBtnText: '🠔 Anterior',
        doneBtnText: 'Entendido ✓',
        progressText: 'Paso {{current}} de {{total}}',
        steps: steps
    });
    
    driverObj.drive();
}
