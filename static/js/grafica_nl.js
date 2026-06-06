/**
 * grafica_nl.js
 * =============
 * Manejo de la gráfica animada para el módulo de Ecuaciones No Lineales.
 * Usa Chart.js para la gráfica y Anime.js para las animaciones premium.
 *
 * Expone:
 *   - renderGraficaNL(datos)   → dibuja/actualiza el chart
 *   - limpiarGraficaNL()       → destruye el chart
 *   - solicitarGraficaNL(...)  → llama a la API y luego renderiza
 */

(function () {
    'use strict';

    let chartInstance = null;      // Instancia global de Chart.js
    let animFrameId   = null;      // Frame de animación activo

    // ─── Paleta "Void Prism" ────────────────────────────────────────────────
    const COLORS = {
        curve:       'rgba(245, 158, 11, 1)',      // Oro — curva f(x)
        curveFill:   'rgba(245, 158, 11, 0.08)',   // Relleno bajo la curva
        steps:       'rgba(6, 182, 212, 1)',        // Cian — puntos de iteración
        stepsFill:   'rgba(6, 182, 212, 0.25)',
        root:        'rgba(16, 185, 129, 1)',        // Verde — raíz encontrada
        rootFill:    'rgba(16, 185, 129, 0.35)',
        zeroline:    'rgba(255, 255, 255, 0.12)',
        grid:        'rgba(255, 255, 255, 0.06)',
        text:        '#a8a29e',
    };

    // ─── Loader / Spinner ───────────────────────────────────────────────────
    function mostrarLoader() {
        const wrapper = document.getElementById('chart-wrapper');
        if (!wrapper) return;
        wrapper.innerHTML = `
            <div id="chart-loader" style="
                display:flex; flex-direction:column; align-items:center;
                justify-content:center; height:100%; gap:16px; color:#a8a29e;
                font-family:'Inter',sans-serif; font-size:14px;">
                <div class="chart-spinner"></div>
                <span>Calculando gráfica…</span>
            </div>`;

        // Animar el spinner con Anime.js
        anime({
            targets: '#chart-loader',
            opacity: [0, 1],
            duration: 400,
            easing: 'easeOutQuad',
        });
    }

    function ocultarLoader() {
        const loader = document.getElementById('chart-loader');
        if (loader) loader.remove();
    }

    // ─── Creación / actualización del canvas ────────────────────────────────
    function prepararCanvas() {
        const wrapper = document.getElementById('chart-wrapper');
        if (!wrapper) return null;

        // Destruir chart anterior si existe
        if (chartInstance) {
            chartInstance.destroy();
            chartInstance = null;
        }

        wrapper.innerHTML = '<canvas id="grafica-nl-canvas"></canvas>';
        return document.getElementById('grafica-nl-canvas');
    }

    // ─── Renderizado principal ──────────────────────────────────────────────
    function renderGraficaNL(datos) {
        const canvas = prepararCanvas();
        if (!canvas) return;

        const { curva, pasos_x, pasos_y, raiz, metodo } = datos;

        // Filtrar nulos de la curva (discontinuidades)
        const curvaData = curva.x.map((x, i) => ({
            x: x,
            y: curva.y[i]
        })).filter(p => p.y !== null && p.y !== undefined);

        const pasosData = pasos_x.map((x, i) => ({ x: x, y: pasos_y[i] }));
        const raizData  = [{ x: raiz, y: 0 }];

        // Anotación de línea cero (y = 0)
        const ceroLineData = [
            { x: curvaData[0]?.x  ?? -10, y: 0 },
            { x: curvaData[curvaData.length - 1]?.x ?? 10, y: 0 },
        ];

        const ctx = canvas.getContext('2d');

        chartInstance = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [
                    {
                        label: 'f(x)',
                        data: curvaData,
                        type: 'line',
                        borderColor: COLORS.curve,
                        backgroundColor: COLORS.curveFill,
                        borderWidth: 2.5,
                        pointRadius: 0,
                        tension: 0.4,
                        fill: true,
                        order: 3,
                    },
                    {
                        label: 'y = 0',
                        data: ceroLineData,
                        type: 'line',
                        borderColor: COLORS.zeroline,
                        backgroundColor: 'transparent',
                        borderWidth: 1,
                        borderDash: [6, 4],
                        pointRadius: 0,
                        order: 4,
                    },
                    {
                        label: 'Iteraciones',
                        data: pasosData,
                        type: 'scatter',
                        backgroundColor: COLORS.stepsFill,
                        borderColor: COLORS.steps,
                        borderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 9,
                        order: 2,
                    },
                    {
                        label: `Raíz ≈ ${window.formatNumber(raiz)}`,
                        data: raizData,
                        type: 'scatter',
                        backgroundColor: COLORS.rootFill,
                        borderColor: COLORS.root,
                        borderWidth: 2.5,
                        pointRadius: 12,
                        pointStyle: 'star',
                        pointHoverRadius: 16,
                        order: 1,
                    },
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 1200,
                    easing: 'easeInOutQuart',
                },
                interaction: {
                    mode: 'nearest',
                    intersect: false,
                    axis: 'xy',
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: COLORS.text,
                            font: { family: "'Inter', sans-serif", size: 12 },
                            boxWidth: 14,
                            padding: 16,
                            usePointStyle: true,
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(17,17,19,0.92)',
                        titleColor: '#f59e0b',
                        bodyColor: '#e5e7eb',
                        borderColor: 'rgba(245,158,11,0.3)',
                        borderWidth: 1,
                        padding: 12,
                        titleFont: { family: "'Outfit', sans-serif", size: 13, weight: '700' },
                        bodyFont:  { family: "'Fira Code', monospace", size: 12 },
                        callbacks: {
                            title: (items) => items[0].dataset.label,
                            label: (item) => ` x = ${window.formatNumber(item.parsed.x)},  f(x) = ${window.formatNumber(item.parsed.y)}`,
                        }
                    },
                },
                scales: {
                    x: {
                        type: 'linear',
                        grid: { color: COLORS.grid },
                        ticks: {
                            color: COLORS.text,
                            font: { family: "'Fira Code', monospace", size: 11 },
                            maxTicksLimit: 10,
                        },
                        title: {
                            display: true,
                            text: 'x',
                            color: '#f59e0b',
                            font: { family: "'Outfit', sans-serif", size: 13, weight: '600' },
                        }
                    },
                    y: {
                        grid: { color: COLORS.grid },
                        ticks: {
                            color: COLORS.text,
                            font: { family: "'Fira Code', monospace", size: 11 },
                        },
                        title: {
                            display: true,
                            text: 'f(x)',
                            color: '#f59e0b',
                            font: { family: "'Outfit', sans-serif", size: 13, weight: '600' },
                        }
                    }
                }
            }
        });

        // ── Animaciones de entrada con Anime.js ─────────────────────────────
        _animarEntradaGrafica();
        _animarPasos(pasos_x.length);
    }

    // ─── Animaciones Anime.js ───────────────────────────────────────────────
    function _animarEntradaGrafica() {
        const panel = document.getElementById('grafica-panel');
        if (!panel) return;

        // Panel completo baja desde arriba con un suave rebote
        anime({
            targets: panel,
            opacity: [0, 1],
            translateY: [-30, 0],
            duration: 700,
            easing: 'easeOutExpo',
        });

        // Borde del panel pulsa con color dorado
        anime({
            targets: panel,
            borderColor: [
                { value: 'rgba(245, 158, 11, 0.55)', duration: 600 },
                { value: 'rgba(245, 158, 11, 0.18)', duration: 600 },
            ],
            loop: false,
            easing: 'easeInOutSine',
        });
    }

    function _animarPasos(n) {
        // Contadores de iteraciones en el badge del título
        const badge = document.getElementById('grafica-iter-badge');
        if (!badge) return;

        let contador = { val: 0 };
        anime({
            targets: contador,
            val: n,
            round: 1,
            duration: 900,
            easing: 'easeOutExpo',
            update: () => { badge.textContent = contador.val; },
        });
    }

    // ─── Petición a la API ──────────────────────────────────────────────────
    async function solicitarGraficaNL(ecuacion, metodo, resultados, angulo) {
        const seccion = document.getElementById('grafica-seccion');
        if (!seccion) return;

        seccion.style.display = 'block';
        mostrarLoader();

        try {
            const res = await fetch('/api/grafica_nl', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ecuacion, metodo, resultados, angulo }),
            });
            const data = await res.json();
            ocultarLoader();

            if (data.error) {
                document.getElementById('chart-wrapper').innerHTML =
                    `<div style="color:#ef4444;text-align:center;padding:40px;font-family:'Inter',sans-serif;">
                        ⚠️ ${data.error}
                    </div>`;
                return;
            }

            renderGraficaNL(data.datos);
        } catch (err) {
            ocultarLoader();
            document.getElementById('chart-wrapper').innerHTML =
                `<div style="color:#ef4444;text-align:center;padding:40px;">
                    Error de conexión: ${err.message}
                </div>`;
        }
    }

    // ─── Limpiar gráfica ────────────────────────────────────────────────────
    function limpiarGraficaNL() {
        if (chartInstance) {
            chartInstance.destroy();
            chartInstance = null;
        }
        const seccion = document.getElementById('grafica-seccion');
        const wrapper = document.getElementById('chart-wrapper');
        if (seccion) {
            anime({
                targets: seccion,
                opacity: [1, 0],
                translateY: [0, 20],
                duration: 400,
                easing: 'easeInQuad',
                complete: () => {
                    seccion.style.display = 'none';
                    seccion.style.opacity = '';
                    seccion.style.transform = '';
                    if (wrapper) wrapper.innerHTML = '';
                }
            });
        }
    }

    // ─── Exportar al scope global ────────────────────────────────────────────
    window.renderGraficaNL    = renderGraficaNL;
    window.limpiarGraficaNL   = limpiarGraficaNL;
    window.solicitarGraficaNL = solicitarGraficaNL;

})();
