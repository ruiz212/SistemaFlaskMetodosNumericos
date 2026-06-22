import { initScene, buildTerrain, drawPaths, resetScene, animateFlight } from './drones_3d.js';

let map;
let markerSalida = null;
let markerEntrega = null;
let simData = null;
let chartInstance = null;

// Referencias DOM
const btnSimular = document.getElementById('btn-simular');
const btnAnimar = document.getElementById('btn-animar');
const btnReset = document.getElementById('btn-reset');
const valSalida = document.getElementById('val-salida');
const valEntrega = document.getElementById('val-entrega');
const btnUbicacion = document.getElementById('btn-ubicacion');
const ledMapa = document.getElementById('led-mapa');
const ledSplines = document.getElementById('led-splines');
const ledSimpson = document.getElementById('led-simpson');

document.addEventListener('DOMContentLoaded', () => {
    initMap();
    initScene('canvas-3d-drones');
    initChart();
    
    btnSimular.addEventListener('click', onSimularClick);
    btnAnimar.addEventListener('click', onAnimarClick);
    btnReset.addEventListener('click', () => {
        resetScene();
        btnAnimar.disabled = !simData;
        updateMetrics(0, 0);
    });
    
    if (btnUbicacion) {
        btnUbicacion.addEventListener('click', irUbicacionActual);
    }
});

function initMap() {
    // Mapa centrado en una ciudad genérica (ej. Nueva York o Madrid)
    map = L.map('map').setView([40.4168, -3.7038], 13);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(map);

    map.on('click', onMapClick);
}

function irUbicacionActual() {
    if (navigator.geolocation) {
        btnUbicacion.innerHTML = '<i class="ph-bold ph-spinner ph-spin"></i>';
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                map.flyTo([lat, lon], 14, { duration: 1.5 });
                btnUbicacion.innerHTML = '<i class="ph-bold ph-navigation-arrow"></i>';
            },
            (error) => {
                showError("Ubicación denegada", "No se pudo acceder a tu ubicación actual. Asegúrate de dar permisos en el navegador.");
                btnUbicacion.innerHTML = '<i class="ph-bold ph-navigation-arrow"></i>';
            }
        );
    } else {
        showError("Geolocalización no soportada", "Tu navegador no soporta la geolocalización.");
    }
}

function onMapClick(e) {
    if (!markerSalida) {
        markerSalida = L.marker(e.latlng).addTo(map)
            .bindPopup("Punto de Salida A").openPopup();
        valSalida.textContent = `${e.latlng.lat.toFixed(4)}, ${e.latlng.lng.toFixed(4)}`;
        ledMapa.classList.add('dr-led--active');
    } else if (!markerEntrega) {
        markerEntrega = L.marker(e.latlng).addTo(map)
            .bindPopup("Punto de Entrega B").openPopup();
        valEntrega.textContent = `${e.latlng.lat.toFixed(4)}, ${e.latlng.lng.toFixed(4)}`;
        btnSimular.disabled = false;
        btnSimular.classList.remove('dr-btn-action--idle');
    } else {
        // Reset
        map.removeLayer(markerSalida);
        map.removeLayer(markerEntrega);
        markerSalida = L.marker(e.latlng).addTo(map)
            .bindPopup("Punto de Salida A").openPopup();
        markerEntrega = null;
        valSalida.textContent = `${e.latlng.lat.toFixed(4)}, ${e.latlng.lng.toFixed(4)}`;
        valEntrega.textContent = "Esperando...";
        btnSimular.disabled = true;
        btnSimular.classList.add('dr-btn-action--idle');
    }
}

async function onSimularClick() {
    btnSimular.disabled = true;
    document.getElementById('btn-simular-text').textContent = "Calculando Trayectoria...";
    ledSplines.classList.add('dr-led--active');
    ledSimpson.classList.add('dr-led--active');
    
    // Validar y obtener coordenadas reales
    if (!markerSalida || !markerEntrega) return;
    
    const startLat = markerSalida.getLatLng().lat;
    const startLon = markerSalida.getLatLng().lng;
    const endLat = markerEntrega.getLatLng().lat;
    const endLon = markerEntrega.getLatLng().lng;
    
    // Validar distancia para no colgar el API OSM (Aprox Haversine)
    const R = 6371; // km
    const dLat = (endLat - startLat) * Math.PI / 180;
    const dLon = (endLon - startLon) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(startLat * Math.PI / 180) * Math.cos(endLat * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    const distKm = R * c;
    
    // No hay límite de distancia, calculamos ruta.

    try {
        const response = await fetch('/aplicacion/api/drones/simular', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start: [startLat, startLon],
                end: [endLat, endLon]
            })
        });

        const data = await response.json();
        
        if (data.success) {
            simData = data;
            
            // Reconstruir 3D
            resetScene();
            buildTerrain(data.terreno.edificios, data.terreno.size, data.terreno.calles || [], data.terreno.manzanas || []);
            drawPaths(data.ruta_cruda, data.ruta_suave);
            
            document.getElementById('val-dist-real').innerHTML = `${data.telemetria.distancia_real.toFixed(1)} <span class="dr-metric__unit">m</span>`;
            
            btnAnimar.disabled = false;
            updateChart(data.telemetria.aceleracion, data.telemetria.velocidad);
        } else {
            showError("Error al calcular", data.error || "Fallo interno");
        }
    } catch (err) {
        showError("Error de Conexión", err.message);
    } finally {
        document.getElementById('btn-simular-text').textContent = "Generar Vuelo Autónomo";
        btnSimular.disabled = false;
        ledSplines.classList.remove('dr-led--active');
        ledSimpson.classList.remove('dr-led--active');
    }
}

function initChart() {
    const ctx = document.getElementById('chart-telemetria').getContext('2d');
    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Aceleración Sensada (m/s²)',
                    data: [],
                    borderColor: 'rgba(6, 182, 212, 1)',
                    backgroundColor: 'rgba(6, 182, 212, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Velocidad (1ra Integral)',
                    data: [],
                    borderColor: 'rgba(16, 185, 129, 1)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: 'rgba(255, 255, 255, 0.7)' } }
            },
            scales: {
                x: { ticks: { color: 'rgba(255, 255, 255, 0.5)' }, grid: { color: 'rgba(255, 255, 255, 0.1)' } },
                y: { ticks: { color: 'rgba(255, 255, 255, 0.5)' }, grid: { color: 'rgba(255, 255, 255, 0.1)' } }
            }
        }
    });
}

function updateChart(accel, vel) {
    const labels = accel.map((_, i) => i);
    chartInstance.data.labels = labels;
    chartInstance.data.datasets[0].data = accel;
    chartInstance.data.datasets[1].data = vel;
    chartInstance.update();
}

function updateMetrics(vel, pos) {
    document.getElementById('val-velocidad').innerHTML = `${vel.toFixed(2)} <span class="dr-metric__unit">m/s</span>`;
    document.getElementById('val-posicion').innerHTML = `${pos.toFixed(2)} <span class="dr-metric__unit">m</span>`;
}

function onAnimarClick() {
    if (!simData) return;
    btnAnimar.disabled = true;
    animateFlight(simData.ruta_suave, simData.telemetria, updateMetrics, () => {
        btnAnimar.disabled = false;
    });
}

function showError(title, msg) {
    document.getElementById('error-title').textContent = title;
    document.getElementById('error-msg').textContent = msg;
    document.getElementById('modal-error').classList.add('active');
}
