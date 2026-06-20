/**
 * tutorial.js
 * Tutorial interactivo con Driver.js — Suite Numérica Pro
 */

document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('tutorial-btn');
    if (btn) btn.addEventListener('click', iniciarTutorial);
});

const DRIVER_CONFIG = {
    showProgress:   true,
    animate:        true,
    popoverClass:   'driverjs-theme',
    nextBtnText:    'Siguiente',
    prevBtnText:    'Anterior',
    doneBtnText:    'Listo',
    progressText:   '{{current}} / {{total}}',
    smoothScroll:   true,
    allowClose:     true,
    overlayOpacity: 0.5,
};

function iniciarTutorial() {
    const driver = window.driver.js.driver;
    const path   = window.location.pathname;

    let steps =
        path === '/' || path === ''         ? stepsIndex()      :
        path.includes('no-lineales')        ? stepsNoLineales() :
        path.includes('polinomios')         ? stepsPolinomios() :
        path.includes('sistemas-lineales')  ? stepsSistemasLineales() :
        path.includes('sistemas')           ? stepsSistemas()   :
        path.includes('iterativos')         ? stepsIterativos() :
        path.includes('interpolacion')      ? stepsInterpolacion() :
        path.includes('integracion')        ? stepsIntegracion() :
        path.includes('aplicacion')         ? stepsAplicacion() :
        stepsGenerico();

    driver({ ...DRIVER_CONFIG, steps }).drive();
}

// ─── INICIO ──────────────────────────────────────────────────────────────────
function stepsIndex() {
    return [
        {
            popover: {
                title: 'Suite Numérica Pro',
                description:
                    'Plataforma para resolver ecuaciones y sistemas no lineales usando ' +
                    'métodos numéricos iterativos. Tiene tres módulos principales que ' +
                    'puedes explorar desde el menú superior.',
            }
        },
        {
            element: '.nav-menu',
            popover: {
                title: 'Módulos disponibles',
                description:
                    '<b>Ecuaciones</b> resuelve f(x) = 0 con una sola variable. ' +
                    '<b>Polinomios</b> encuentra todas las raíces de un polinomio, ' +
                    'incluyendo raíces complejas. ' +
                    '<b>Sistemas</b> resuelve n ecuaciones con n variables.',
                side: 'bottom'
            }
        },
        {
            element: '#theme-btn',
            popover: {
                title: 'Tema visual',
                description:
                    'Cambia entre modo oscuro y modo claro. ' +
                    'La preferencia se guarda automáticamente.',
                side: 'left'
            }
        },
        {
            element: '.modules-grid',
            popover: {
                title: 'Acceso rápido',
                description:
                    'Cada tarjeta describe brevemente qué métodos incluye el módulo. ' +
                    'Haz clic en cualquiera para comenzar.',
                side: 'top'
            }
        },
    ];
}

// ─── ECUACIONES NO LINEALES ───────────────────────────────────────────────────
function stepsNoLineales() {
    const steps = [
        {
            popover: {
                title: 'Buscador de raíces',
                description:
                    'Encuentra el valor de <code>x</code> donde <code>f(x) = 0</code>. ' +
                    'Elige el método según los datos que tengas disponibles y la función a analizar.',
            }
        },
        {
            element: '#ecuacion-nl',
            popover: {
                title: 'Ecuación f(x)',
                description:
                    'Escribe la función usando sintaxis estándar de Python. ' +
                    'Usa <code>**</code> para potencias y <code>*</code> para multiplicar.<br><br>' +
                    'Puedes usar: <code>sin</code>, <code>cos</code>, <code>exp</code>, ' +
                    '<code>ln</code>, <code>sqrt</code>, entre otras.<br>' +
                    'Ejemplo: <code>x**3 - 2*x - 5</code> o <code>cos(x) - x</code>',
                side: 'bottom'
            }
        },
        {
            element: '#metodo-nl',
            popover: {
                title: 'Método de solución',
                description:
                    '<b>Bisección y Regla Falsa</b> requieren un intervalo [a, b] donde la ' +
                    'función cambie de signo. Son robustos pero más lentos.<br><br>' +
                    '<b>Newton-Raphson</b> converge muy rápido con un solo punto inicial, ' +
                    'pero necesita que la derivada exista y no sea cero.<br><br>' +
                    '<b>Secante</b> es similar a Newton pero usa dos puntos en lugar de la derivada. ' +
                    '<b>Punto Fijo</b> itera sobre g(x) = x.',
                side: 'bottom'
            }
        },
        {
            element: '#angulo-nl',
            popover: {
                title: 'Sistema de ángulos',
                description:
                    'Aplica solo si usas funciones trigonométricas. ' +
                    'En matemáticas el estándar son radianes. ' +
                    'Si tu función está definida en grados, selecciona esa opción ' +
                    'y el sistema hará la conversión automáticamente.',
                side: 'bottom'
            }
        },
        {
            element: '#tol-nl',
            popover: {
                title: 'Tolerancia',
                description:
                    'Porcentaje de error relativo máximo aceptado para detener el método:<br><br>' +
                    '<code>Eₐ = |x_nuevo − x_anterior| / |x_nuevo| × 100%</code><br><br>' +
                    'Cuando este valor baja de la tolerancia, el algoritmo se detiene. ' +
                    'Un valor típico es <code>0.01</code> (0.01%).',
                side: 'bottom'
            }
        },
        {
            element: '#campos-dinamicos-nl',
            popover: {
                title: 'Parámetros del método',
                description:
                    'Los campos cambian según el método seleccionado.<br><br>' +
                    'Bisección y Regla Falsa piden los límites <code>a</code> y <code>b</code>, ' +
                    'donde f(a) y f(b) deben tener signos opuestos.<br>' +
                    'Newton-Raphson pide un punto inicial <code>ci</code>.<br>' +
                    'Secante pide dos puntos <code>x0</code> y <code>x1</code>.',
                side: 'top'
            }
        },
        {
            element: '.form-actions',
            popover: {
                title: 'Ejecutar el cálculo',
                description:
                    '<b>Calcular</b> ejecuta el método iterativo y muestra la tabla de resultados ' +
                    'junto con la gráfica de la función.<br><br>' +
                    '<b>Limpiar</b> reinicia todos los campos.',
                side: 'top'
            }
        },
        {
            element: '.table-container',
            popover: {
                title: 'Tabla de iteraciones',
                description:
                    'Muestra el proceso completo, una fila por iteración. ' +
                    'La última columna es el error relativo porcentual. ' +
                    'La primera iteración no tiene error porque no hay punto anterior de comparación.',
                side: 'top'
            }
        },
        {
            element: '#resultado-nl',
            popover: {
                title: 'Resultado',
                description: 'La raíz encontrada con 8 cifras decimales de precisión.',
                side: 'top'
            }
        },
    ];

    // El paso de la gráfica solo se muestra si ya existe un cálculo previo
    const graficaPanel = document.getElementById('grafica-seccion');
    if (graficaPanel && graficaPanel.style.display !== 'none') {
        steps.push({
            element: '#grafica-seccion',
            popover: {
                title: 'Gráfica de la función',
                description:
                    'Muestra la curva completa de f(x) en el rango relevante, ' +
                    'con los puntos de cada iteración marcados y la raíz señalada. ' +
                    'El rango del eje X se determina automáticamente según el dominio válido.',
                side: 'top'
            }
        });
    } else {
        steps.push({
            popover: {
                title: 'Gráfica de la función',
                description:
                    'Después de calcular aparece una gráfica con la curva de f(x), ' +
                    'los puntos de cada iteración y la raíz encontrada. ' +
                    'Vuelve a abrir el tutorial tras el primer cálculo para ver ese paso en detalle.'
            }
        });
    }

    return steps;
}

// ─── POLINOMIOS ───────────────────────────────────────────────────────────────
function stepsPolinomios() {
    return [
        {
            popover: {
                title: 'Raíces de polinomios',
                description:
                    'Calcula todas las raíces de un polinomio de grado n, ' +
                    'incluyendo raíces complejas que no son posibles con los métodos del módulo de Ecuaciones.',
            }
        },
        {
            element: '#metodo-pol',
            popover: {
                title: 'Método',
                description:
                    '<b>Bairstow</b> extrae pares de raíces usando factores cuadráticos. ' +
                    'Es el más completo para polinomios.<br><br>' +
                    '<b>Müller</b> ajusta una parábola a tres puntos y puede encontrar ' +
                    'raíces complejas. También funciona con funciones no polinomiales.<br><br>' +
                    '<b>Horner-Newton</b> combina la evaluación eficiente de Horner con ' +
                    'Newton-Raphson. Ideal cuando ya sabes la zona aproximada de una raíz.',
                side: 'bottom'
            }
        },
        {
            element: '#grupo-grado',
            popover: {
                title: 'Grado del polinomio',
                description:
                    'El exponente más alto del polinomio. ' +
                    'Al cambiar este valor, el sistema genera los campos de coeficientes correspondientes.',
                side: 'bottom'
            }
        },
        {
            element: '#tol-pol',
            popover: {
                title: 'Tolerancia',
                description:
                    'Error relativo porcentual de parada. ' +
                    'Valores típicos: <code>1</code> para resultados rápidos, ' +
                    '<code>0.001</code> para mayor precisión.',
                side: 'bottom'
            }
        },
        {
            element: '#seccion-coeficientes',
            popover: {
                title: 'Coeficientes',
                description:
                    'Ingresa los coeficientes de mayor a menor grado.<br><br>' +
                    'Para <code>2x³ − x² + 4x − 8</code> sería: ' +
                    'a₃ = 2, a₂ = −1, a₁ = 4, a₀ = −8.<br>' +
                    'Si un término no existe, escribe <code>0</code>.',
                side: 'top'
            }
        },
        {
            element: '#campos-dinamicos-pol',
            popover: {
                title: 'Valores iniciales',
                description:
                    'Bairstow acepta r₀ y s₀ opcionales — si se dejan vacíos el sistema elige automáticamente.<br>' +
                    'Müller requiere tres puntos x₀, x₁, x₂.<br>' +
                    'Horner-Newton requiere un valor inicial r₀ ' +
                    '(puede ser complejo, por ejemplo <code>1+2j</code>).',
                side: 'top'
            }
        },
        {
            element: '.form-actions',
            popover: {
                title: 'Calcular',
                description:
                    'El sistema realiza las iteraciones y muestra la tabla de convergencia. ' +
                    'En la consola inferior aparecen las raíces finales con sus valores reales e imaginarios.',
                side: 'top'
            }
        },
        {
            element: '#consola-pol',
            popover: {
                title: 'Consola de resultados',
                description:
                    'Muestra las raíces finales encontradas. ' +
                    'Las raíces complejas aparecen en pares conjugados: ' +
                    '<code>1.2 + 3.5j</code> y <code>1.2 − 3.5j</code>.',
                side: 'top'
            }
        },
    ];
}

// ─── SISTEMAS NO LINEALES ─────────────────────────────────────────────────────
function stepsSistemas() {
    return [
        {
            popover: {
                title: 'Sistemas no lineales',
                description:
                    'Resuelve sistemas de n ecuaciones con n variables usando ' +
                    'Newton-Raphson multivariable. El sistema calcula automáticamente ' +
                    'la matriz Jacobiana (derivadas parciales) en cada iteración.',
            }
        },
        {
            element: '#n-sis',
            popover: {
                title: 'Número de variables',
                description:
                    'Define cuántas ecuaciones y variables tiene el sistema (mínimo 2, máximo 10). ' +
                    'Al cambiar este valor se generan automáticamente los campos para cada función y valor inicial.',
                side: 'bottom'
            }
        },
        {
            element: '#tol-sis',
            popover: {
                title: 'Tolerancia',
                description:
                    'El método se detiene cuando el cambio máximo entre el vector X anterior ' +
                    'y el nuevo es menor a este valor: <code>max(|X_nuevo − X|) &lt; tol</code>.',
                side: 'bottom'
            }
        },
        {
            element: '#iter-sis',
            popover: {
                title: 'Máximo de iteraciones',
                description:
                    'Límite de seguridad para casos en que el sistema no converge. ' +
                    'Si el Jacobiano se vuelve singular o el punto inicial está muy lejos ' +
                    'de la solución, el método puede divergir. Este límite garantiza que pare.',
                side: 'bottom'
            }
        },
        {
            element: '#container-sis',
            popover: {
                title: 'Ecuaciones y valores iniciales',
                description:
                    'Para cada ecuación fᵢ hay dos campos: la función igualada a cero ' +
                    'y el valor inicial de esa variable.<br><br>' +
                    'Ejemplo: <code>x**2 + y**2 - 4</code> con valor inicial <code>1.5</code>.<br><br>' +
                    'Mientras más cerca esté el valor inicial de la solución real, más rápido converge.',
                side: 'top'
            }
        },
        {
            element: '.form-actions',
            popover: {
                title: 'Calcular',
                description:
                    'El sistema parsea las ecuaciones, detecta las variables automáticamente, ' +
                    'construye el Jacobiano simbólico con SymPy y ejecuta las iteraciones de Newton.',
                side: 'top'
            }
        },
        {
            element: '#consola-sis',
            popover: {
                title: 'Registro y solución',
                description:
                    'Muestra el proceso completo: la Jacobiana evaluada en cada iteración ' +
                    'y la solución final con los valores de cada variable.',
                side: 'top'
            }
        },
    ];
}

// ─── SISTEMAS LINEALES ────────────────────────────────────────────────────────
function stepsSistemasLineales() {
    return [
        {
            popover: {
                title: 'Sistemas Lineales',
                description:
                    'Resuelve sistemas de ecuaciones de la forma <b>Ax = b</b>. ' +
                    'Puedes usar métodos directos de descomposición o eliminación.',
            }
        },
        {
            element: '#n-lin',
            popover: {
                title: 'Dimensión (n)',
                description:
                    'Indica el número de incógnitas y ecuaciones. ' +
                    'La matriz se redimensionará automáticamente al cambiar este valor.',
                side: 'bottom'
            }
        },
        {
            element: '#metodo-lin',
            popover: {
                title: 'Método de solución',
                description:
                    '<b>Eliminación Gaussiana</b>: Transforma A en una matriz triangular superior.<br><br>' +
                    '<b>Factorización LU</b>: Descompone A en matrices L (Lower) y U (Upper).<br><br>' +
                    '<b>Regla de Cramer</b>: Usa determinantes (solo para sistemas pequeños).<br><br>' +
                    '<b>Matriz Inversa</b>: Calcula x = A⁻¹b.',
                side: 'bottom'
            }
        },
        {
            element: '#matrix-container',
            popover: {
                title: 'Matriz A y Vector b',
                description:
                    'Ingresa los coeficientes de la matriz en los cuadros blancos ' +
                    'y los términos independientes en los cuadros resaltados a la derecha.<br><br>' +
                    'Usa números reales o enteros.',
                side: 'top'
            }
        },
        {
            element: '#btn-calc-lin',
            popover: {
                title: 'Resolver',
                description:
                    'Ejecuta el algoritmo seleccionado y muestra el vector solución ' +
                    'junto con el desglose paso a paso del proceso matemático.',
                side: 'top'
            }
        },
        {
            element: '#resultado-lin-container',
            popover: {
                title: 'Resultados y Pasos',
                description:
                    'Aquí aparecerá la solución final (X) y las matrices intermedias ' +
                    'generadas durante el cálculo (como la matriz escalonada o las matrices L y U).',
                side: 'top'
            }
        },
    ];
}

// ─── ITERATIVOS (SISTEMAS LINEALES) ──────────────────────────────────────────
function stepsIterativos() {
    return [
        {
            popover: {
                title: 'Métodos Iterativos',
                description: 'Resuelve sistemas lineales Ax=b mediante aproximaciones sucesivas (Jacobi y Gauss-Seidel).',
            }
        },
        {
            element: '#metodo-lin',
            popover: {
                title: 'Método Iterativo',
                description: 'Selecciona Jacobi o Gauss-Seidel. Gauss-Seidel usa los valores calculados inmediatamente, lo que suele hacer que converja más rápido.',
                side: 'bottom'
            }
        },
        {
            element: '#matrix-container',
            popover: {
                title: 'Matriz A y Vector b',
                description: 'Ingresa los coeficientes. Recuerda que para asegurar la convergencia, la matriz A debe ser preferiblemente diagonalmente dominante.',
                side: 'top'
            }
        },
        {
            element: '#vector-inicial-container',
            popover: {
                title: 'Vector Inicial (x0)',
                description: 'El vector donde inicia la iteración. Generalmente se rellena con ceros, pero puedes poner otros valores si estás cerca de la solución.',
                side: 'top'
            }
        },
        {
            element: '.form-actions',
            popover: {
                title: 'Calcular',
                description: 'Ejecuta el método iterativo. El proceso se detendrá al alcanzar la tolerancia o el máximo de iteraciones.',
                side: 'top'
            }
        }
    ];
}

// ─── INTERPOLACIÓN ────────────────────────────────────────────────────────────
function stepsInterpolacion() {
    return [
        {
            popover: {
                title: 'Interpolación Numérica',
                description: 'Ajusta una curva que pase exactamente por un conjunto de puntos (X, Y) para estimar valores intermedios.',
            }
        },
        {
            element: '#metodo-int',
            popover: {
                title: 'Método de Interpolación',
                description: 'Selecciona Newton (Diferencias Divididas) o Lagrange. Ambos matemáticamente llegan al mismo polinomio, pero usan algoritmos distintos.',
                side: 'bottom'
            }
        },
        {
            element: '#puntos-container',
            popover: {
                title: 'Puntos de Datos',
                description: 'Ingresa los valores de X y Y. Puedes agregar más puntos cambiando el número de datos arriba.',
                side: 'top'
            }
        },
        {
            element: '#x-eval',
            popover: {
                title: 'Valor a evaluar (Opcional)',
                description: 'Ingresa un valor específico de X para calcular cuánto valdría Y en esa posición de la curva interpolada.',
                side: 'top'
            }
        },
        {
            element: '.form-actions',
            popover: {
                title: 'Calcular',
                description: 'Calcula el polinomio interpolador y te muestra su gráfica pasando por todos los puntos.',
                side: 'top'
            }
        }
    ];
}

// ─── INTEGRACIÓN NUMÉRICA ─────────────────────────────────────────────────────
function stepsIntegracion() {
    return [
        {
            popover: {
                title: 'Integración Numérica',
                description: 'Calcula el área bajo la curva de una función o resuelve integrales dobles usando métodos numéricos.',
            }
        },
        {
            element: '#ecuacion',
            popover: {
                title: 'Función a Integrar',
                description: 'Escribe la función matemática f(x) que deseas integrar. Usa sintaxis de Python (ej. sin(x) + e**x).',
                side: 'bottom'
            }
        },
        {
            element: '#metodo',
            popover: {
                title: 'Método',
                description: 'Trapecio aproxima el área usando trapecios. Romberg utiliza la extrapolación de Richardson para obtener resultados mucho más precisos.',
                side: 'bottom'
            }
        },
        {
            element: '#a_val',
            popover: {
                title: 'Límites',
                description: 'Establece el rango desde dónde hasta dónde quieres calcular el área bajo la curva.',
                side: 'top'
            }
        },
        {
            element: '.form-actions',
            popover: {
                title: 'Calcular',
                description: 'Resuelve la integral definida numéricamente y muestra el proceso iterativo y la sumatoria final.',
                side: 'top'
            }
        }
    ];
}

// ─── APLICACIÓN IOT (PANEL SOLAR) ─────────────────────────────────────────────
function stepsAplicacion() {
    return [
        {
            popover: {
                title: 'Simulador de Panel Solar',
                description: 'Aplica los métodos numéricos en un caso real: Optimizando la energía de un panel solar usando datos satelitales.',
            }
        },
        {
            element: '#map',
            popover: {
                title: 'Ubicación Geográfica',
                description: 'Haz clic en cualquier parte del mapa. Esto obtendrá los datos de irradiancia solar y temperatura de ese punto desde la API de Open-Meteo.',
                side: 'right'
            }
        },
        {
            element: '#panel-coef',
            popover: {
                title: 'Hardware Termodinámico',
                description: 'Diferentes paneles pierden distinta cantidad de energía por el calor. Selecciona el hardware a simular.',
                side: 'bottom'
            }
        },
        {
            element: '#btn-simular',
            popover: {
                title: 'Motor Numérico',
                description: 'Al ejecutar, el backend usa Newton-Raphson para hallar el ángulo óptimo y la Regla del Trapecio para integrar el total de energía diaria.',
                side: 'bottom'
            }
        },
        {
            element: '#panel-resultados',
            popover: {
                title: 'Resultados y Gráfica Dual',
                description: 'Muestra los resultados matemáticos calculados y dibuja la gráfica comparando la energía ideal (STC) con la real afectada por el calor.',
                side: 'left'
            }
        },
        {
            element: '#panel-3d-container',
            popover: {
                title: 'Gemelo Digital 3D',
                description: 'Visualiza la inclinación exacta que calculó el método de Newton-Raphson aplicada a un modelo 3D del panel. Puedes rotar la escena con el mouse.',
                side: 'left'
            }
        }
    ];
}

// ─── FALLBACK ─────────────────────────────────────────────────────────────────
function stepsGenerico() {
    return [{
        popover: {
            title: 'Suite Numérica Pro',
            description: 'Usa el menú superior para navegar a uno de los módulos y ver el tutorial de esa sección.'
        }
    }];
}
