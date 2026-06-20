/* ==========================================================================
   PANEL SOLAR IoT — JavaScript v2.0 (Senior Engineering)
   Features: ResizeObserver map fix, toast notifications, animated counters,
             LED status indicators, explicit button states, copy feedback
   ========================================================================== */

let map;
let marker;
let chart;
let currentLat = 0;
let currentLon = 0;

// ═══════════════════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    initMap();
    initMapObserver();
});

function initMap() {
    // Fix Leaflet default icon paths (they resolve incorrectly under Flask blueprints)
    delete L.Icon.Default.prototype._getIconUrl;
    L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png'
    });

    map = L.map('map').setView([0, -78], 4);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);

    // Map click handler
    map.on('click', function(e) {
        currentLat = e.latlng.lat;
        currentLon = e.latlng.lng;

        if (marker) {
            map.removeLayer(marker);
        }
        marker = L.marker([currentLat, currentLon]).addTo(map);

        // Update coordinates with animation
        animateCoordUpdate('lat-val', currentLat.toFixed(4) + '°');
        animateCoordUpdate('lon-val', currentLon.toFixed(4) + '°');

        // Update IoT endpoint
        const baseUrl = window.location.origin;
        document.getElementById('iot-endpoint').innerText =
            `${baseUrl}/aplicacion/api/iot/angulo_actual?lat=${currentLat.toFixed(4)}&lon=${currentLon.toFixed(4)}`;

        // Enable button
        const btn = document.getElementById('btn-simular');
        btn.disabled = false;
        setButtonState('idle');
        btn.classList.add('ps-pulse');

        // Update LED: ubicación → active
        setLed('led-ubicacion', 'active');

        showToast('Ubicación seleccionada correctamente', 'success');
    });
}

// Use ResizeObserver instead of fragile setTimeout for map invalidation
function initMapObserver() {
    const mapContainer = document.getElementById('map');
    if (!mapContainer || !map) return;

    const observer = new ResizeObserver(() => {
        map.invalidateSize();
    });
    observer.observe(mapContainer);

    // Also invalidate once when the page-transition-wrapper finishes its animation
    const wrapper = document.querySelector('.page-transition-wrapper');
    if (wrapper) {
        wrapper.addEventListener('transitionend', () => {
            map.invalidateSize();
        }, { once: true });
    }

    // Safety fallback — invalidate after a very short delay anyway
    requestAnimationFrame(() => {
        setTimeout(() => map.invalidateSize(), 100);
    });
}

// ═══════════════════════════════════════════════════════════════════════════
// SIMULATION
// ═══════════════════════════════════════════════════════════════════════════

async function simularPanel() {
    const btn = document.getElementById('btn-simular');
    btn.classList.remove('ps-pulse');
    setButtonState('loading');
    showSkeletons(true);

    // LEDs
    setLed('led-api', 'warning');
    setLed('led-calculo', 'idle');

    try {
        // Obtenemos el coeficiente térmico seleccionado por el usuario
        const coefSelect = document.getElementById('panel-coef');
        const coeficiente = coefSelect ? parseFloat(coefSelect.value) : -0.45;

        const payload = { 
            lat: currentLat, 
            lon: currentLon,
            coef: coeficiente
        };

        const response = await fetch('/aplicacion/api/simular', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        // API responded
        setLed('led-api', 'active');

        if (!data.success) {
            setLed('led-calculo', 'error');
            setButtonState('idle');
            showSkeletons(false);
            showToast('Error: ' + data.error, 'error');
            return;
        }

        // Calculation complete
        setLed('led-calculo', 'active');

        // Show results with animated counters
        showSkeletons(false);
        animateValue('res-angulo', 0, parseFloat(data.angulo_optimo), 900, '°');
        // Fix NaN bug: Usar energia_real
        animateValue('res-energia', 0, parseFloat(data.energia_real), 1100, ' Wh');

        // Draw chart with two curves
        dibujarGrafica(data.clima, data.curva_real, data.energia_perdida);
        
        // Actualizar Gemelo Digital 3D
        if (window.actualizarModelo3D) {
            window.actualizarModelo3D(parseFloat(data.angulo_optimo));
        }

        setButtonState('success');
        showToast('Simulación completada exitosamente', 'success');

        // Reset button after 2.5s
        setTimeout(() => {
            setButtonState('idle');
        }, 2500);

    } catch (error) {
        console.error(error);
        setLed('led-api', 'error');
        setLed('led-calculo', 'error');
        setButtonState('idle');
        showSkeletons(false);
        showToast('Error de conexión con el servidor', 'error');
    }
}

// Make simularPanel globally available
window.simularPanel = simularPanel;

// ═══════════════════════════════════════════════════════════════════════════
// BUTTON STATES
// ═══════════════════════════════════════════════════════════════════════════

function setButtonState(state) {
    const btn = document.getElementById('btn-simular');
    const textEl = document.getElementById('btn-simular-text');
    const iconContainer = btn.querySelector('i, .ps-spinner');

    // Remove all state classes
    btn.classList.remove('ps-btn-action--idle', 'ps-btn-action--loading', 'ps-btn-action--success');

    // Remove existing spinner if any
    const existingSpinner = btn.querySelector('.ps-spinner');
    if (existingSpinner) existingSpinner.remove();

    // Remove existing icon if replaced
    const existingIcon = btn.querySelector('i');

    switch (state) {
        case 'idle':
            btn.classList.add('ps-btn-action--idle');
            btn.disabled = false;
            textEl.textContent = 'Ejecutar Simulación Numérica';
            if (existingIcon) {
                existingIcon.className = 'ph-bold ph-cpu';
            } else {
                const icon = document.createElement('i');
                icon.className = 'ph-bold ph-cpu';
                btn.insertBefore(icon, textEl);
            }
            break;

        case 'loading':
            btn.classList.add('ps-btn-action--loading');
            btn.disabled = true;
            textEl.textContent = 'Procesando...';
            if (existingIcon) existingIcon.remove();
            const spinner = document.createElement('span');
            spinner.className = 'ps-spinner';
            spinner.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" opacity="0.3"/>
                <path d="M12 2v4"/>
            </svg>`;
            btn.insertBefore(spinner, textEl);
            break;

        case 'success':
            btn.classList.add('ps-btn-action--success');
            btn.disabled = false;
            textEl.textContent = '¡Simulación Completa!';
            if (existingIcon) {
                existingIcon.className = 'ph-bold ph-check-circle';
            } else {
                const icon = document.createElement('i');
                icon.className = 'ph-bold ph-check-circle';
                btn.insertBefore(icon, textEl);
            }
            break;
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// LED STATUS INDICATORS
// ═══════════════════════════════════════════════════════════════════════════

function setLed(ledId, state) {
    const led = document.getElementById(ledId);
    if (!led) return;
    led.className = 'ps-led';
    switch (state) {
        case 'idle':    led.classList.add('ps-led--idle'); break;
        case 'warning': led.classList.add('ps-led--warning'); break;
        case 'active':  led.classList.add('ps-led--active'); break;
        case 'error':   led.classList.add('ps-led--error'); break;
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// ANIMATED VALUE COUNTER
// ═══════════════════════════════════════════════════════════════════════════

function animateValue(elementId, start, end, duration, suffix) {
    const el = document.getElementById(elementId);
    if (!el) return;

    // Remove waiting badge if present
    el.innerHTML = '';

    const startTime = performance.now();
    const isDecimal = end % 1 !== 0;

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Ease out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        const currentVal = start + (end - start) * eased;

        el.textContent = (isDecimal ? currentVal.toFixed(2) : Math.round(currentVal)) + suffix;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

// ═══════════════════════════════════════════════════════════════════════════
// SKELETON LOADERS
// ═══════════════════════════════════════════════════════════════════════════

function showSkeletons(show) {
    const anguloVal = document.getElementById('res-angulo');
    const energiaVal = document.getElementById('res-energia');

    if (show) {
        anguloVal.innerHTML = '<div class="ps-metric__value--skeleton"></div>';
        energiaVal.innerHTML = '<div class="ps-metric__value--skeleton"></div>';
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// COORDINATE ANIMATION
// ═══════════════════════════════════════════════════════════════════════════

function animateCoordUpdate(elementId, newValue) {
    const el = document.getElementById(elementId);
    if (!el) return;

    el.style.transition = 'opacity 0.15s ease, transform 0.15s ease';
    el.style.opacity = '0';
    el.style.transform = 'translateY(-4px)';

    setTimeout(() => {
        el.textContent = newValue;
        el.style.opacity = '1';
        el.style.transform = 'translateY(0)';
    }, 150);
}

// ═══════════════════════════════════════════════════════════════════════════
// TOAST NOTIFICATIONS
// ═══════════════════════════════════════════════════════════════════════════

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `ps-toast ps-toast--${type}`;

    const icons = {
        success: 'ph-fill ph-check-circle',
        error: 'ph-fill ph-warning-circle',
        info: 'ph-fill ph-info'
    };

    toast.innerHTML = `
        <i class="ps-toast__icon ${icons[type] || icons.info}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Auto-dismiss after 4s
    setTimeout(() => {
        toast.classList.add('ps-toast--out');
        toast.addEventListener('animationend', () => toast.remove());
    }, 4000);
}

// ═══════════════════════════════════════════════════════════════════════════
// CHART
// ═══════════════════════════════════════════════════════════════════════════

function dibujarGrafica(datosHorarios, curvaReal = null, energiaPerdida = 0) {
    const canvas = document.getElementById('solarChart');
    const emptyState = document.getElementById('chart-empty-state');
    const ctx = canvas.getContext('2d');

    // Show canvas, hide empty state
    emptyState.style.display = 'none';
    canvas.style.display = 'block';

    if (chart) {
        chart.destroy();
    }

    const labels = datosHorarios.map(d => d.hora);
    const dataIdeal = datosHorarios.map(d => d.radiacion);
    
    // Si no tenemos curva real, la hacemos igual a la ideal
    const dataReal = curvaReal || dataIdeal;

    // Premium gradient para curva ideal (amarilla)
    let gradientIdeal = ctx.createLinearGradient(0, 0, 0, canvas.parentElement.clientHeight);
    gradientIdeal.addColorStop(0, 'rgba(245, 158, 11, 0.25)');
    gradientIdeal.addColorStop(1, 'rgba(245, 158, 11, 0.0)');
    
    // Premium gradient para curva real (roja)
    let gradientReal = ctx.createLinearGradient(0, 0, 0, canvas.parentElement.clientHeight);
    gradientReal.addColorStop(0, 'rgba(239, 68, 68, 0.45)');
    gradientReal.addColorStop(1, 'rgba(239, 68, 68, 0.0)');

    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Radiación Ideal (STC)',
                    data: dataIdeal,
                    borderColor: '#f59e0b',
                    backgroundColor: gradientIdeal,
                    borderWidth: 1.5,
                    borderDash: [5, 5],
                    pointRadius: 0, 
                    fill: true,
                    tension: 0.4
                },
                {
                    label: `Radiación Real (-${energiaPerdida} Wh térmicos)`,
                    data: dataReal,
                    borderColor: '#ef4444',
                    backgroundColor: gradientReal,
                    borderWidth: 2.5,
                    pointBackgroundColor: '#fff',
                    pointBorderColor: '#ef4444',
                    pointBorderWidth: 2,
                    pointRadius: 3,
                    pointHoverRadius: 6,
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#e2e8f0',
                        font: { family: "'Inter', sans-serif", size: 12 },
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(9,9,11,0.92)',
                    borderColor: 'rgba(245,158,11,0.3)',
                    borderWidth: 1,
                    titleFont: { family: "'Inter', sans-serif", size: 13, weight: '600' },
                    bodyFont: { family: "'Fira Code', monospace", size: 12 },
                    cornerRadius: 10,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(ctx) {
                            return `${ctx.parsed.y.toFixed(1)} W/m²`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#94a3b8',
                        font: { size: 11 },
                        maxTicksLimit: 12
                    },
                    grid: { color: 'rgba(255,255,255,0.04)' }
                },
                y: {
                    ticks: {
                        color: '#94a3b8',
                        font: { size: 11 }
                    },
                    grid: { color: 'rgba(255,255,255,0.04)' },
                    title: {
                        display: true,
                        text: 'Irradiancia (W/m²)',
                        color: '#94a3b8',
                        font: { family: "'Inter', sans-serif", size: 12, weight: '500' }
                    }
                }
            },
            animation: {
                duration: 1200,
                easing: 'easeOutQuart'
            }
        }
    });
}

// ═══════════════════════════════════════════════════════════════════════════
// IoT COPY
// ═══════════════════════════════════════════════════════════════════════════

function copiarEndpointIoT() {
    const endpoint = document.getElementById('iot-endpoint').innerText;
    if (!endpoint.includes('http')) {
        showToast('Primero selecciona una ubicación en el mapa', 'info');
        return;
    }

    navigator.clipboard.writeText(endpoint).then(() => {
        const card = document.getElementById('iot-card');
        card.classList.add('ps-iot-card--copied');
        showToast('Endpoint IoT copiado al portapapeles', 'success');

        setTimeout(() => {
            card.classList.remove('ps-iot-card--copied');
        }, 1500);
    }).catch(() => {
        showToast('No se pudo copiar al portapapeles', 'error');
    });
}

// Make copy function globally available
window.copiarEndpointIoT = copiarEndpointIoT;

// ═══════════════════════════════════════════════════════════════════════════
// GEOLOCATION
// ═══════════════════════════════════════════════════════════════════════════

function irUbicacionActual() {
    if (!navigator.geolocation) {
        showToast('Geolocalización no soportada por el navegador', 'error');
        return;
    }

    showToast('Obteniendo ubicación...', 'info');

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;

            // Update map view
            map.setView([lat, lon], 12);

            // Simulate a click event on the map to trigger the existing logic
            map.fire('click', {
                latlng: L.latLng(lat, lon)
            });
            
            showToast('Ubicación actual anclada con éxito', 'success');
        },
        (error) => {
            console.error(error);
            showToast('No se pudo obtener la ubicación. Verifica los permisos.', 'error');
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
}

window.irUbicacionActual = irUbicacionActual;

// Attach click handler to the simulate button
document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('btn-simular');
    if (btn) {
        btn.addEventListener('click', simularPanel);
    }
});
