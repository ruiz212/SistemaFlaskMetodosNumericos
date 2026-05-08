/**
 * tutorial.js
 * ===========
 * Tutorial interactivo con Driver.js para la Suite Numérica Pro.
 * Cada página tiene su propio set de pasos contextuales con explicaciones
 * detalladas de cada campo, botón y sección.
 */

document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('tutorial-btn');
    if (btn) {
        btn.addEventListener('click', iniciarTutorial);
    }
});

// ─── Configuración global de Driver.js ───────────────────────────────────────
const DRIVER_CONFIG = {
    showProgress:   true,
    animate:        true,
    popoverClass:   'driverjs-theme',
    nextBtnText:    'Siguiente →',
    prevBtnText:    '← Anterior',
    doneBtnText:    '✓ Entendido',
    progressText:   'Paso {{current}} de {{total}}',
    smoothScroll:   true,
    allowClose:     true,
    overlayOpacity: 0.55,
};

// ─── Función principal ────────────────────────────────────────────────────────
function iniciarTutorial() {
    const driver = window.driver.js.driver;
    const path   = window.location.pathname;

    let steps = [];

    if (path === '/' || path === '' || path === '/index.html') {
        steps = stepsIndex();
    } else if (path.includes('no-lineales')) {
        steps = stepsNoLineales();
    } else if (path.includes('polinomios')) {
        steps = stepsPolinomios();
    } else if (path.includes('sistemas')) {
        steps = stepsSistemas();
    } else {
        steps = stepsGenerico();
    }

    const driverObj = driver({ ...DRIVER_CONFIG, steps });
    driverObj.drive();
}

// ═══════════════════════════════════════════════════════════════════════════════
// PÁGINA DE INICIO
// ═══════════════════════════════════════════════════════════════════════════════
function stepsIndex() {
    return [
        {
            popover: {
                title: '👋 Bienvenido a la Suite Numérica Pro',
                description:
                    'Esta plataforma implementa los principales <b>métodos numéricos iterativos</b> ' +
                    'para encontrar raíces de ecuaciones y resolver sistemas. ' +
                    'Te daré un recorrido rápido por todo lo que puedes hacer.',
            }
        },
        {
            element: '.brand',
            popover: {
                title: '🔢 Suite Numérica',
                description:
                    'El logo Σ representa la suma de todos los métodos numéricos integrados: ' +
                    '<b>Bisección, Regla Falsa, Newton-Raphson, Secante, Punto Fijo, ' +
                    'Müller, Bairstow, Horner-Newton</b> y <b>Sistemas No Lineales</b>.',
                side: 'bottom', align: 'start'
            }
        },
        {
            element: '.nav-menu',
            popover: {
                title: '🧭 Menú de Navegación',
                description:
                    'Desde aquí accedes a los <b>3 módulos principales</b>:<br><br>' +
                    '📐 <b>Ecuaciones</b> — Raíces de f(x)=0 con una variable<br>' +
                    '📊 <b>Polinomios</b> — Raíces reales y complejas de polinomios<br>' +
                    '🔗 <b>Sistemas</b> — Newton-Raphson multivariable (n ecuaciones)',
                side: 'bottom'
            }
        },
        {
            element: '#theme-btn',
            popover: {
                title: '🌙 Modo Oscuro / Claro',
                description:
                    'Cambia entre el <b>tema oscuro (Void)</b> y el <b>tema claro</b>. ' +
                    'Tu preferencia se guarda automáticamente en el navegador.',
                side: 'left'
            }
        },
        {
            element: '#tutorial-btn',
            popover: {
                title: '❓ Botón de Tutorial',
                description:
                    'En <b>cualquier página</b> puedes hacer clic en este ícono de pregunta ' +
                    'para lanzar el tutorial contextual. Cada módulo tiene su propio tour explicativo.',
                side: 'left'
            }
        },
        {
            element: '.modules-grid',
            popover: {
                title: '🚀 Acceso Rápido a Módulos',
                description:
                    'Haz clic en cualquiera de estas tarjetas para ir directamente al módulo. ' +
                    'Cada tarjeta describe brevemente qué métodos incluye y para qué tipo de ' +
                    'problema sirve.',
                side: 'top'
            }
        },
    ];
}

// ═══════════════════════════════════════════════════════════════════════════════
// PÁGINA: ECUACIONES NO LINEALES
// ═══════════════════════════════════════════════════════════════════════════════
function stepsNoLineales() {
    const steps = [
        {
            popover: {
                title: '📐 Buscador de Raíces — f(x) = 0',
                description:
                    'Este módulo encuentra la <b>raíz de una función</b>, es decir, el valor de ' +
                    '<code>x</code> tal que <b>f(x) = 0</b>.<br><br>' +
                    'Disponible para funciones con <b>1 sola variable</b> usando métodos iterativos. ' +
                    'Al terminar el cálculo, verás la tabla de iteraciones <b>y una gráfica animada</b> de la función.',
            }
        },
        {
            element: '#ecuacion-nl',
            popover: {
                title: '1️⃣ Ecuación f(x)',
                description:
                    'Escribe tu función usando Python/SymPy. Ejemplos válidos:<br><br>' +
                    '• <code>x**3 - 2*x - 5</code><br>' +
                    '• <code>x + ln(x)</code><br>' +
                    '• <code>cos(x) - x</code><br>' +
                    '• <code>exp(x) - 3*x</code><br><br>' +
                    '⚠️ Usa <code>**</code> para potencias, <code>*</code> para multiplicar. ' +
                    'Puedes escribir <code>X</code> o <code>x</code> — el sistema los trata igual.',
                side: 'bottom'
            }
        },
        {
            element: '#metodo-nl',
            popover: {
                title: '2️⃣ Método Numérico',
                description:
                    'Selecciona el algoritmo según lo que tengas disponible:<br><br>' +
                    '• <b>Bisección</b> — Necesita intervalo [a,b] con cambio de signo. Lento pero seguro.<br>' +
                    '• <b>Regla Falsa</b> — Como Bisección, pero usa interpolación lineal. Más rápido.<br>' +
                    '• <b>Newton-Raphson</b> — Solo necesita un punto. Muy rápido. Usa la derivada.<br>' +
                    '• <b>Secante</b> — Como Newton pero sin derivada analítica. Usa 2 puntos.<br>' +
                    '• <b>Punto Fijo</b> — Necesita |g\'(x)| &lt; 1 para converger.',
                side: 'bottom'
            }
        },
        {
            element: '#angulo-nl',
            popover: {
                title: '3️⃣ Sistema de Ángulos',
                description:
                    'Si usas funciones trigonométricas (<code>sin</code>, <code>cos</code>, <code>tan</code>...):<br><br>' +
                    '• <b>Radianes</b> — Estándar matemático (recomendado)<br>' +
                    '• <b>Grados</b> — El sistema convierte automáticamente: sin(x°) → sin(x·π/180)<br><br>' +
                    'Si tu función no tiene trigonométricas, este campo no afecta el resultado.',
                side: 'bottom'
            }
        },
        {
            element: '#tol-nl',
            popover: {
                title: '4️⃣ Tolerancia (Error %)',
                description:
                    'Es el <b>error relativo porcentual máximo</b> aceptable para detener el método:<br><br>' +
                    '<code>Eₐ = |x_nuevo - x_anterior| / |x_nuevo| × 100%</code><br><br>' +
                    'El algoritmo para cuando <b>Eₐ &lt; tolerancia</b>.<br>' +
                    'Ejemplo: <code>0.01</code> = parar cuando el error sea menor al 0.01%.',
                side: 'bottom'
            }
        },
        {
            element: '#campos-dinamicos-nl',
            popover: {
                title: '5️⃣ Parámetros del Método',
                description:
                    'Estos campos cambian según el método elegido:<br><br>' +
                    '• <b>Bisección/Regla Falsa</b> → Límite inferior <code>a</code> y superior <code>b</code> ' +
                    '(f(a) y f(b) deben tener signos opuestos)<br>' +
                    '• <b>Newton-Raphson</b> → Punto inicial <code>ci</code><br>' +
                    '• <b>Secante</b> → Dos puntos iniciales <code>x0</code> y <code>x1</code><br>' +
                    '• <b>Punto Fijo</b> → Punto inicial <code>x0</code>',
                side: 'top'
            }
        },
        {
            element: '.form-actions',
            popover: {
                title: '6️⃣ Calcular y Limpiar',
                description:
                    '• <b>Calcular</b> → Ejecuta el método y muestra la tabla de iteraciones más la gráfica.<br>' +
                    '• <b>Limpiar</b> → Resetea todos los campos y oculta la gráfica (con animación de papelera).',
                side: 'top'
            }
        },
        {
            element: '.table-container',
            popover: {
                title: '📋 Tabla de Iteraciones',
                description:
                    'Muestra el proceso iterativo completo, fila por fila:<br><br>' +
                    '• Cada fila = una iteración del método<br>' +
                    '• La última columna es el <b>error relativo %</b><br>' +
                    '• La primera iteración muestra <code>---</code> (no hay punto anterior aún)<br>' +
                    '• El método para cuando el error es menor a la tolerancia ingresada.',
                side: 'top'
            }
        },
        {
            element: '#resultado-nl',
            popover: {
                title: '✅ Resultado Final',
                description:
                    'Aquí aparece la <b>raíz encontrada</b> con 8 decimales de precisión ' +
                    'y el nombre del método que convergió.',
                side: 'top'
            }
        },
        {
            element: '#btn-exportar-nl',
            popover: {
                title: '📥 Exportar a Excel',
                description:
                    'Descarga la tabla de iteraciones en formato <b>CSV</b> (compatible con Excel). ' +
                    'Se activa automáticamente después de calcular.',
                side: 'top'
            }
        },
    ];

    // Paso de la gráfica: condicional según si ya hay un cálculo realizado
    const graficaPanel = document.getElementById('grafica-seccion');
    if (graficaPanel && graficaPanel.style.display !== 'none') {
        steps.push({
            element: '#grafica-seccion',
            popover: {
                title: '📈 Gráfica Animada de f(x)',
                description:
                    'Panel de visualización de la función:<br><br>' +
                    '🟡 <b>Línea dorada</b> → Curva completa de f(x)<br>' +
                    '🔵 <b>Puntos cian</b> → Iteraciones del método<br>' +
                    '⭐ <b>Estrella verde</b> → Raíz encontrada<br>' +
                    '🔢 <b>Badge naranja</b> → Contador animado de iteraciones<br><br>' +
                    'El rango del eje X se calcula automáticamente según el dominio válido de f(x).',
                side: 'top'
            }
        });
    } else {
        steps.push({
            popover: {
                title: '📈 Gráfica de la Función',
                description:
                    'Después de hacer clic en <b>Calcular</b>, aparece un panel de gráfica animado ' +
                    'mostrando la curva de f(x), los puntos de cada iteración y la raíz encontrada.<br><br>' +
                    '💡 Vuelve a abrir el tutorial <b>después de calcular</b> para ver la explicación de la gráfica.'
            }
        });
    }

    return steps;
}

// ═══════════════════════════════════════════════════════════════════════════════
// PÁGINA: POLINOMIOS
// ═══════════════════════════════════════════════════════════════════════════════
function stepsPolinomios() {
    return [
        {
            popover: {
                title: '📊 Raíces de Polinomios',
                description:
                    'Este módulo calcula las <b>raíces de polinomios</b>, incluyendo raíces ' +
                    '<b>complejas (imaginarias)</b> que los métodos del módulo de Ecuaciones no pueden encontrar.<br><br>' +
                    'Trabaja directamente con los <b>coeficientes</b> del polinomio:<br>' +
                    '<code>P(x) = aₙxⁿ + aₙ₋₁xⁿ⁻¹ + ... + a₁x + a₀</code>',
            }
        },
        {
            element: '#metodo-pol',
            popover: {
                title: '1️⃣ Método',
                description:
                    'Tres algoritmos disponibles según el tipo de raíces que buscas:<br><br>' +
                    '• <b>Bairstow</b> — Extrae pares de raíces (reales o complejas conjugadas) del polinomio usando factores cuadráticos. Ideal para polinomios de grado par.<br><br>' +
                    '• <b>Müller</b> — Ajusta una parábola a 3 puntos. Puede encontrar raíces complejas y funciona con funciones no polinomiales.<br><br>' +
                    '• <b>Horner-Newton</b> — Newton-Raphson optimizado con evaluación de Horner. Rápido pero puede dar raíces complejas solo si el punto inicial es complejo.',
                side: 'bottom'
            }
        },
        {
            element: '#grupo-grado',
            popover: {
                title: '2️⃣ Grado del Polinomio',
                description:
                    'Define el <b>exponente más alto</b> del polinomio.<br><br>' +
                    'Ejemplo: para <code>3x⁴ - x³ + 2x - 5</code>, el grado es <b>4</b>.<br><br>' +
                    'Al cambiar el grado, el sistema genera automáticamente los campos para ingresar los coeficientes a₄, a₃, a₂, a₁, a₀.',
                side: 'bottom'
            }
        },
        {
            element: '#tol-pol',
            popover: {
                title: '3️⃣ Tolerancia',
                description:
                    'Error relativo porcentual de parada.<br><br>' +
                    'Valores típicos: <code>1</code> (1%) para resultados rápidos, ' +
                    '<code>0.001</code> (0.001%) para alta precisión.',
                side: 'bottom'
            }
        },
        {
            element: '#seccion-coeficientes',
            popover: {
                title: '4️⃣ Coeficientes del Polinomio',
                description:
                    'Ingresa los coeficientes de mayor a menor grado:<br><br>' +
                    'Para <code>P(x) = 2x³ - x² + 4x - 8</code>:<br>' +
                    '• a₃ = <code>2</code><br>' +
                    '• a₂ = <code>-1</code><br>' +
                    '• a₁ = <code>4</code><br>' +
                    '• a₀ = <code>-8</code><br><br>' +
                    '⚠️ Si un término no existe, ingresa <code>0</code>.',
                side: 'top'
            }
        },
        {
            element: '#campos-dinamicos-pol',
            popover: {
                title: '5️⃣ Valores Iniciales (según método)',
                description:
                    '• <b>Bairstow</b> → r₀ y s₀ opcionales (el sistema elige automáticamente si se dejan vacíos)<br>' +
                    '• <b>Müller</b> → 3 puntos iniciales x₀, x₁, x₂<br>' +
                    '• <b>Horner-Newton</b> → Un valor inicial r₀ (puede ser complejo, ej: <code>1+2j</code>)',
                side: 'top'
            }
        },
        {
            element: '.form-actions',
            popover: {
                title: '6️⃣ Ejecutar',
                description:
                    '• <b>Calcular</b> → El sistema itera, extrae raíces y muestra la tabla de convergencia.<br>' +
                    '• <b>Limpiar</b> → Resetea todo incluyendo coeficientes y consola.',
                side: 'top'
            }
        },
        {
            element: '#thead-pol',
            popover: {
                title: '📋 Tabla de Convergencia',
                description:
                    'Muestra cómo el método converge hacia cada raíz:<br><br>' +
                    '• <b>Bairstow</b> → Iteraciones de r y s (coeficientes del factor cuadrático)<br>' +
                    '• <b>Müller</b> → Parabola ajustada en cada paso con xi, xi+1<br>' +
                    '• <b>Horner-Newton</b> → División sintética iterativa (esquema de Horner)',
                side: 'top'
            }
        },
        {
            element: '#consola-pol',
            popover: {
                title: '🖥️ Consola de Resultados',
                description:
                    'Aquí aparecen las <b>raíces finales encontradas</b> junto con el proceso detallado:<br><br>' +
                    '• Para raíces reales: <code>x = 2.5000</code><br>' +
                    '• Para raíces complejas: <code>x = 1.2 + 3.5j</code> y su conjugada <code>x = 1.2 - 3.5j</code>',
                side: 'top'
            }
        },
    ];
}

// ═══════════════════════════════════════════════════════════════════════════════
// PÁGINA: SISTEMAS NO LINEALES
// ═══════════════════════════════════════════════════════════════════════════════
function stepsSistemas() {
    return [
        {
            popover: {
                title: '🔗 Sistemas No Lineales',
                description:
                    'Resuelve sistemas de <b>n ecuaciones no lineales con n variables</b> usando ' +
                    '<b>Newton-Raphson Multivariable</b>.<br><br>' +
                    'Ejemplo para n=2:<br>' +
                    '<code>f₁(x,y) = x² + y² - 4 = 0</code><br>' +
                    '<code>f₂(x,y) = x - y + 1 = 0</code><br><br>' +
                    'El sistema calcula la <b>matriz Jacobiana</b> automáticamente usando SymPy.',
            }
        },
        {
            element: '#n-sis',
            popover: {
                title: '1️⃣ Número de Variables (n)',
                description:
                    'Define cuántas ecuaciones y variables tiene el sistema.<br><br>' +
                    '• Mínimo: <b>2</b> variables<br>' +
                    '• Máximo: <b>10</b> variables<br><br>' +
                    'Al cambiar este valor, el sistema genera automáticamente los campos para las n ecuaciones y sus n valores iniciales.',
                side: 'bottom'
            }
        },
        {
            element: '#angulo-sis',
            popover: {
                title: '2️⃣ Sistema de Ángulos',
                description:
                    'Igual que en Ecuaciones No Lineales: si tus funciones usan ' +
                    '<code>sin</code>, <code>cos</code>, etc., elige el sistema de ángulos.<br><br>' +
                    'Por defecto usa <b>Radianes</b>.',
                side: 'bottom'
            }
        },
        {
            element: '#tol-sis',
            popover: {
                title: '3️⃣ Tolerancia (Error)',
                description:
                    'El método para cuando el cambio máximo entre el vector X anterior y el nuevo es menor a este valor:<br><br>' +
                    '<code>max(|X_nuevo - X|) &lt; tolerancia</code><br><br>' +
                    'Valor típico: <code>0.001</code> o <code>0.0001</code>.',
                side: 'bottom'
            }
        },
        {
            element: '#iter-sis',
            popover: {
                title: '4️⃣ Máximo de Iteraciones',
                description:
                    '<b>Obligatorio.</b> Limita el número de iteraciones para evitar bucles infinitos cuando el sistema diverge.<br><br>' +
                    'Si el Jacobiano es singular en algún punto o el vector inicial está muy lejos de la solución, ' +
                    'el método puede no converger. Este límite garantiza que el cálculo termine.<br><br>' +
                    'Valor recomendado: <code>25</code> a <code>100</code>.',
                side: 'bottom'
            }
        },
        {
            element: '#container-sis',
            popover: {
                title: '5️⃣ Ecuaciones y Valores Iniciales',
                description:
                    'Para cada ecuación fᵢ tienes dos campos:<br><br>' +
                    '• <b>fᵢ</b> — La ecuación igualada a cero. Usa las variables que correspondan (x, y, z o x₁, x₂...).<br>' +
                    '  Ejemplo: <code>x**2 + y**2 - 4</code><br><br>' +
                    '• <b>xᵢ</b> — Valor inicial de esa variable. El método arranca desde aquí.<br>' +
                    '  Ejemplo: <code>1.5</code><br><br>' +
                    '⚠️ Mientras más cerca el valor inicial esté de la solución real, más rápido converge.',
                side: 'top'
            }
        },
        {
            element: '.form-actions',
            popover: {
                title: '6️⃣ Calcular',
                description:
                    'Al hacer clic en <b>Calcular</b>, el sistema:<br><br>' +
                    '1. Parsea todas las ecuaciones con SymPy<br>' +
                    '2. Detecta las variables automáticamente<br>' +
                    '3. Calcula la <b>matriz Jacobiana</b> (derivadas parciales) simbólicamente<br>' +
                    '4. En cada iteración: invierte J y aplica <code>X_nuevo = X - J⁻¹·F(X)</code><br>' +
                    '5. Para cuando el error máximo &lt; tolerancia',
                side: 'top'
            }
        },
        {
            element: '#thead-sis',
            popover: {
                title: '📋 Tabla de Iteraciones',
                description:
                    'Cada columna es una variable del sistema:<br><br>' +
                    '• <b>Iteración</b> — Número de paso<br>' +
                    '• <b>x, y, z...</b> — Valor de cada variable en esa iteración<br>' +
                    '• <b>Error</b> — Máximo cambio entre iteraciones consecutivas<br><br>' +
                    'La solución converge cuando todos los valores se estabilizan.',
                side: 'top'
            }
        },
        {
            element: '#consola-sis',
            popover: {
                title: '🖥️ Registro y Solución Final',
                description:
                    'Muestra el proceso completo en formato de consola:<br><br>' +
                    '• Las <b>matrices Jacobianas</b> en cada iteración<br>' +
                    '• La <b>solución final</b>: x₁ = ..., x₂ = ...<br>' +
                    '• Si no converge, indica en qué iteración el Jacobiano se volvió singular.',
                side: 'top'
            }
        },
        {
            element: '#btn-exportar-sis',
            popover: {
                title: '📥 Exportar a Excel',
                description:
                    'Descarga la tabla de iteraciones como archivo <b>CSV</b> para analizarla en Excel.',
                side: 'top'
            }
        },
    ];
}

// ═══════════════════════════════════════════════════════════════════════════════
// FALLBACK
// ═══════════════════════════════════════════════════════════════════════════════
function stepsGenerico() {
    return [
        {
            popover: {
                title: '🧭 Explora la Suite Numérica',
                description:
                    'Usa el menú superior para navegar a uno de los tres módulos y obtener ' +
                    'un tutorial detallado de ese módulo específico.',
            }
        }
    ];
}
