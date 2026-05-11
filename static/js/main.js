/**
 * Suite Numérica Pro - Main Logic
 * Refactored for maintainability, performance, and UX.
 */

// ─── Utilities ───────────────────────────────────────────────────────────────

function showAlert(title, text, icon) {
    Swal.fire({
        title: title,
        text: text,
        icon: icon,
        background: '#1e293b',
        color: '#f8fafc',
        confirmButtonColor: '#6366f1'
    });
    if (icon === 'success') playSound('success');
    else if (icon === 'error' || icon === 'warning') playSound('error');
}

/**
 * Sistema de Sonidos Sutiles
 */
function playSound(type) {
    const context = new (window.AudioContext || window.webkitAudioContext)();
    const osc = context.createOscillator();
    const gain = context.createGain();

    osc.connect(gain);
    gain.connect(context.destination);

    const now = context.currentTime;

    if (type === 'success') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(523.25, now); // C5
        osc.frequency.exponentialRampToValueAtTime(1046.50, now + 0.1); // C6
        gain.gain.setValueAtTime(0.1, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
        osc.start(now);
        osc.stop(now + 0.3);
    } else if (type === 'error') {
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(150, now);
        osc.frequency.linearRampToValueAtTime(100, now + 0.2);
        gain.gain.setValueAtTime(0.1, now);
        gain.gain.linearRampToValueAtTime(0.01, now + 0.2);
        osc.start(now);
        osc.stop(now + 0.2);
    } else if (type === 'clean') {
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(800, now);
        osc.frequency.exponentialRampToValueAtTime(400, now + 0.1);
        gain.gain.setValueAtTime(0.1, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.1);
        osc.start(now);
        osc.stop(now + 0.1);
    }
}

/**
 * Centered Request Handler
 * Handles loading states and errors globally.
 */
async function performRequest(url, payload, buttonId) {
    const btn = buttonId ? document.getElementById(buttonId) : null;
    let originalText = "";
    
    if (btn) {
        originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = `<i class="ph-bold ph-spinner-gap spin"></i> Procesando...`;
    }

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Request failed:", error);
        showAlert("Error de Conexión", "No se pudo contactar con el servidor.", "error");
        return { error: error.message };
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    }
}

function exportarExcel(tablaId, nombreArchivo) {
    const table = document.getElementById(tablaId);
    if (!table) return;
    const rows = Array.from(table.querySelectorAll('tr'));
    
    const csvContent = rows.map(row => {
        const cols = Array.from(row.querySelectorAll('td, th'));
        return cols.map(col => {
            let data = col.innerText.replace(/(\r\n|\n|\r)/gm, '').replace(/(\s\s)/gm, ' ');
            return `"${data.replace(/"/g, '""')}"`;
        }).join(',');
    }).join('\n');
    
    const blob = new Blob(["\ufeff", csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${nombreArchivo}_${new Date().getTime()}.csv`;
    link.click();
    URL.revokeObjectURL(url);
}

/**
 * Previsualización de Matemáticas en Tiempo Real
 */
function previewMath(inputId, previewId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    if (!input || !preview) return;

    let text = input.value.trim();
    if (!text) {
        preview.innerHTML = '';
        return;
    }

    // Solución Senior: Usar math.js para parsear y convertir a LaTeX real
    // Esto maneja fracciones anidadas, potencias y todo automáticamente.
    let latex = "";
    try {
        // Limpiar un poco el texto antes de math.js (ej. ** -> ^)
        let cleanText = text.replace(/\*\*/g, '^');
        
        // Parsear con mathjs
        const node = math.parse(cleanText);
        latex = node.toTex({
            parenthesis: 'keep', // Mantener coherencia con lo que escribe el usuario
            implicit: 'show'     // Mostrar multiplicaciones implícitas
        });

        // Correcciones menores de formato KaTeX
        latex = latex
            .replace(/\\cdot/g, ' \\cdot ')
            .replace(/\\ln/g, '\\ln')
            .replace(/\\exp/g, 'e^{') // exp(x) -> e^{x}
            // mathjs pone a veces paréntesis de más en exp, limpiamos si es necesario
            .replace(/e\^\{([^}]+)\}/g, (m, p1) => `e^{${p1}}`);

        // Estilo HUD activo
        preview.classList.add('active');
        
        katex.render(latex, preview, {
            throwOnError: false,
            displayMode: true
        });
    } catch (e) {
        // Si falla el parseo (mientras escribe), mostrar algo sutil o el regex anterior como fallback
        preview.innerHTML = `<small style="color:rgba(255,255,255,0.4)">Escribiendo estructura...</small>`;
        // No ocultamos el panel para evitar parpadeo
    }
}

/**
 * Exportación a PDF Profesional
 */
async function exportarPDF(elementId, filename) {
    const { jsPDF } = window.jspdf;
    const element = document.getElementById(elementId);
    if (!element) return;

    const btn = document.activeElement;
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<i class="ph-bold ph-spinner-gap spin"></i> Generando...`;

    try {
        const canvas = await html2canvas(element, {
            scale: 2,
            useCORS: true,
            backgroundColor: '#0f172a'
        });
        
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF('p', 'mm', 'a4');
        const imgProps = pdf.getImageProperties(imgData);
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
        
        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
        pdf.save(`${filename}.pdf`);
        playSound('success');
    } catch (e) {
        console.error(e);
        showAlert("Error", "No se pudo generar el PDF", "error");
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

/**
 * Generador de Snippets de Código
 */
function generarCodigoSnippet(metodo, payload) {
    let code = "";
    if (['Bisección', 'Regla Falsa', 'Newton-Raphson', 'Secante'].includes(metodo)) {
        code = `
import math

def f(x):
    return ${payload.ecuacion.replace(/\*\*/g, '**')}

def resolver():
    # Implementación básica de ${metodo}
    # Tolerancia: ${payload.tol}%
    print("Calculando ${metodo} para f(x)...")
    # ... lógica del método ...

resolver()
        `;
    }
    
    const container = document.getElementById('seccion-codigo');
    const snippet = document.getElementById('codigo-snippet');
    if (container && snippet) {
        container.style.display = 'block';
        snippet.querySelector('code').textContent = code.trim();
    }
}

function copyCode() {
    const code = document.getElementById('codigo-snippet').textContent;
    navigator.clipboard.writeText(code).then(() => {
        Swal.fire({
            toast: true,
            position: 'top-end',
            icon: 'success',
            title: 'Código copiado',
            showConfirmButton: false,
            timer: 1500,
            background: '#1e293b',
            color: '#fff'
        });
    });
}

// ─── Ecuaciones No Lineales ──────────────────────────────────────────────────

function actualizarCamposNL() {
    const metodo = document.getElementById('metodo-nl')?.value;
    const container = document.getElementById('campos-dinamicos-nl');
    if (!container) return;

    let html = '';
    switch(metodo) {
        case 'Bisección':
        case 'Regla Falsa':
            html = `
                <div class="input-group flex-1"><label>Límite Inferior (a):</label><input type="text" id="nl-a" class="input-control"></div>
                <div class="input-group flex-1"><label>Límite Superior (b):</label><input type="text" id="nl-b" class="input-control"></div>`;
            break;
        case 'Newton-Raphson':
            html = `<div class="input-group flex-1"><label>Punto inicial (ci):</label><input type="text" id="nl-ci" class="input-control"></div>`;
            break;
        case 'Secante':
            html = `
                <div class="input-group flex-1"><label>Punto x0:</label><input type="text" id="nl-x0" class="input-control"></div>
                <div class="input-group flex-1"><label>Punto x1:</label><input type="text" id="nl-x1" class="input-control"></div>`;
            break;
        case 'Punto fijo':
            html = `<div class="input-group flex-1"><label>Punto inicial (x0):</label><input type="text" id="nl-x0" class="input-control"></div>`;
            break;
    }
    container.innerHTML = html;
}

async function calcularNL(force = false) {
    const fields = {
        ecuacion: document.getElementById('ecuacion-nl')?.value,
        metodo: document.getElementById('metodo-nl')?.value,
        tol: document.getElementById('tol-nl')?.value,
        angulo: document.getElementById('angulo-nl')?.value || 'rad'
    };
    
    if (!fields.ecuacion || !fields.tol) return showAlert('Atención', 'Ingresa una ecuación y la tolerancia.', 'warning');

    const payload = { ...fields, force };
    
    // Recolección dinámica de parámetros según el método
    if (['Bisección', 'Regla Falsa'].includes(fields.metodo)) {
        payload.a = document.getElementById('nl-a')?.value;
        payload.b = document.getElementById('nl-b')?.value;
    } else if (fields.metodo === 'Newton-Raphson') {
        payload.ci = document.getElementById('nl-ci')?.value;
    } else if (fields.metodo === 'Secante') {
        payload.x0 = document.getElementById('nl-x0')?.value;
        payload.x1 = document.getElementById('nl-x1')?.value;
    } else if (fields.metodo === 'Punto fijo') {
        payload.x0 = document.getElementById('nl-x0')?.value;
    }

    // Validación básica de campos requeridos
    if (Object.values(payload).some(v => v === "")) return showAlert('Atención', 'Por favor, complete todos los campos.', 'warning');

    const data = await performRequest('/api/calcular_nl', payload, 'btn-calc-nl');
    
    if (data.warning) {
        Swal.fire({
            title: 'Validación',
            text: data.warning,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Sí, continuar',
            cancelButtonText: 'No',
            background: '#1e293b',
            color: '#f8fafc'
        }).then((result) => { if (result.isConfirmed) calcularNL(true); });
        return;
    }
    
    if (data.error) return showAlert('Error', data.error, 'error');
    
    window._lastResultadosNL = data.resultados;
    window._lastMetodoNL     = fields.metodo;
    
    renderTablaNL(data.resultados, fields.metodo);
    const resultDiv = document.getElementById('resultado-nl');
    if (resultDiv) {
        resultDiv.textContent = data.mensaje;
        resultDiv.className = 'resultado-tarjeta flex-3 text-center success';
    }
    document.getElementById('btn-exportar-nl').disabled = false;
    if (document.getElementById('btn-pdf-nl')) document.getElementById('btn-pdf-nl').disabled = false;

    generarCodigoSnippet(fields.metodo, payload);
    salvarHistorial(fields.metodo, payload);
    playSound('success');
}

function renderTablaNL(resultados, metodo) {
    const thead = document.getElementById('thead-nl');
    const tbody = document.getElementById('tbody-nl');
    if (!thead || !tbody) return;
    
    let headers = '';
    let rows = '';

    if (['Bisección', 'Regla Falsa'].includes(metodo)) {
        headers = `<th>It</th><th>a</th><th>b</th><th>c</th><th>f(a)</th><th>f(b)</th><th>f(c)</th><th>f(a)*f(c)</th><th>Er%</th>`;
        rows = resultados.map(r => `<tr><td>${r.iter}</td><td>${r.a}</td><td>${r.b}</td><td>${r.c}</td><td>${r.fa}</td><td>${r.fb}</td><td>${r.fc}</td><td>${r.prueba}</td><td>${r.error}</td></tr>`).join('');
    } else if (metodo === 'Newton-Raphson') {
        headers = `<th>It</th><th>ci</th><th>f(ci)</th><th>f'(ci)</th><th>ci+1</th><th>Er%</th>`;
        rows = resultados.map(r => `<tr><td>${r.iter}</td><td>${r.ci}</td><td>${r.fci}</td><td>${r.dfci}</td><td>${r.cimas1}</td><td>${r.error}</td></tr>`).join('');
    } else if (metodo === 'Secante') {
        headers = `<th>It</th><th>Ci</th><th>f(ci)</th><th>Er%</th>`;
        rows = resultados.map(r => `<tr><td>${r.iter}</td><td>${r.ci}</td><td>${r.fci}</td><td>${r.error}</td></tr>`).join('');
    } else if (metodo === 'Punto fijo') {
        headers = `<th>It</th><th>Ci</th><th>g(Ci)</th><th>Er%</th>`;
        rows = resultados.map(r => `<tr><td>${r.iter}</td><td>${r.ci}</td><td>${r.gci}</td><td>${r.error}</td></tr>`).join('');
    }

    thead.innerHTML = headers;
    tbody.innerHTML = rows;
    if (window.animarTabla) window.animarTabla('#tabla-nl');
}

function limpiarNL() {
    playSound('clean');
    animarLimpieza(() => {
        ['ecuacion-nl', 'tol-nl'].forEach(id => { const el = document.getElementById(id); if(el) el.value = ''; });
        document.getElementById('thead-nl').innerHTML = '';
        document.getElementById('tbody-nl').innerHTML = '';
        const preview = document.getElementById('preview-nl');
        if (preview) {
            preview.innerHTML = '';
            preview.classList.remove('active');
        }
        const codeSec = document.getElementById('seccion-codigo');
        if (codeSec) codeSec.style.display = 'none';

        const res = document.getElementById('resultado-nl');
        if (res) {
            res.textContent = 'Esperando parámetros...';
            res.className = 'resultado-tarjeta flex-3 text-center';
        }
        document.getElementById('btn-exportar-nl').disabled = true;
        if (document.getElementById('btn-pdf-nl')) document.getElementById('btn-pdf-nl').disabled = true;
        actualizarCamposNL();
    });
}

// ─── Polinomios ──────────────────────────────────────────────────────────────

function generarCamposCoeficientes() {
    const grado = parseInt(document.getElementById('grado-pol')?.value || 0);
    const container = document.getElementById('container-coefs');
    if (!container) return;
    
    container.innerHTML = Array.from({length: grado + 1}, (_, i) => grado - i).map(i => `
        <div class="input-group" style="opacity: 0;">
            <label style="color: var(--accent-blue); font-weight: 600;">a_${i}</label>
            <input type="text" id="coef-${i}" class="input-control text-center">
        </div>`).join('');

    if (window.anime) {
        anime({
            targets: '#container-coefs .input-group',
            scale: [0.9, 1],
            opacity: [0, 1],
            delay: anime.stagger(50),
            duration: 500,
            easing: 'easeOutBack'
        });
    }
}

function actualizarCamposPol() {
    const metodo = document.getElementById('metodo-pol')?.value;
    const container = document.getElementById('campos-dinamicos-pol');
    if (!container) return;
    
    const seccionCoefs = document.getElementById('seccion-coeficientes');
    const grupoGrado = document.getElementById('grupo-grado');
    const grupoEq = document.getElementById('grupo-ecuacion-pol');

    // Siempre mostramos coeficientes para Muller, Bairstow y Horner
    if (seccionCoefs) seccionCoefs.style.display = 'block';
    if (grupoGrado) grupoGrado.style.display = 'flex';
    if (grupoEq) grupoEq.style.display = 'none';

    let html = '';
    if (metodo === 'Müller') {
        html = `
            <div class="input-group flex-1"><label>x0:</label><input type="text" id="pol-x0" class="input-control"></div>
            <div class="input-group flex-1"><label>x1:</label><input type="text" id="pol-x1" class="input-control"></div>
            <div class="input-group flex-1"><label>x2:</label><input type="text" id="pol-x2" class="input-control"></div>`;
    } else if (metodo === 'Horner-Newton') {
        html = `<div class="input-group flex-1"><label>r0 inicial:</label><input type="text" id="pol-r0" class="input-control"></div>`;
    } else if (metodo === 'Bairstow') {
        html = `
            <div class="input-group flex-1"><label>r0 (opcional):</label><input type="text" id="pol-r0-bair" class="input-control" placeholder="Auto"></div>
            <div class="input-group flex-1"><label>s0 (opcional):</label><input type="text" id="pol-s0-bair" class="input-control" placeholder="Auto"></div>`;
    }
    container.innerHTML = html;
}

async function calcularPol() {
    const metodo = document.getElementById('metodo-pol')?.value;
    const tol = document.getElementById('tol-pol')?.value;
    const payload = { metodo, tol };

    if (metodo === 'Müller') {
        payload.x0 = document.getElementById('pol-x0')?.value;
        payload.x1 = document.getElementById('pol-x1')?.value;
        payload.x2 = document.getElementById('pol-x2')?.value;
    }

    // Coeficientes
    const grado = parseInt(document.getElementById('grado-pol')?.value || 0);
    const coeficientes = [];
    for (let i = grado; i >= 0; i--) {
        const val = document.getElementById(`coef-${i}`)?.value;
        if (!val) return showAlert('Atención', `Falta el coeficiente a_${i}`, 'warning');
        try { coeficientes.push(math.evaluate(val)); } catch { return showAlert('Error', `Sintaxis inválida en a_${i}`, 'error'); }
    }
    payload.coeficientes = coeficientes;

    if (metodo === 'Horner-Newton') {
        payload.r0 = document.getElementById('pol-r0')?.value;
    } else if (metodo === 'Bairstow') {
        const r0 = document.getElementById('pol-r0-bair')?.value;
        const s0 = document.getElementById('pol-s0-bair')?.value;
        if (r0) payload.r0 = r0;
        if (s0) payload.s0 = s0;
    }

    const data = await performRequest('/api/calcular_pol', payload, 'btn-calc-pol');
    
    if (data.consola) document.getElementById('consola-pol').value = data.consola;
    if (data.error) return showAlert('Error', data.error, 'error');
    
    if (metodo === 'Bairstow' && data.r_init !== undefined) {
        document.getElementById('pol-r0-bair').value = data.r_init.toFixed(4);
        document.getElementById('pol-s0-bair').value = data.s_init.toFixed(4);
    }
    
    renderTablaPol(data.resultados, metodo, data.encabezados);
    document.getElementById('btn-exportar-pol').disabled = false;
}

function renderTablaPol(resultados, metodo, encabezados) {
    const thead = document.getElementById('thead-pol');
    const tbody = document.getElementById('tbody-pol');
    if (!thead || !tbody) return;

    if (metodo === 'Müller') {
        thead.innerHTML = `<tr><th>i</th><th>X_i</th><th>X_{i+1}</th><th>h_i</th><th>h_{i+1}</th><th>f(X_i)</th><th>f(X_{i+1})</th><th>δ_i</th><th>δ_{i+1}</th><th>a</th><th>b</th><th>c</th><th>b+√</th><th>b-√</th><th>Error %</th></tr>`;
        tbody.innerHTML = resultados.map(r => `<tr><td>${r.iter}</td><td>${r.x1}</td><td>${r.x2}</td><td>${r.h0}</td><td>${r.h1}</td><td>${r.f1}</td><td>${r.f2}</td><td>${r.d0}</td><td>${r.d1}</td><td>${r.a}</td><td>${r.b}</td><td>${r.c}</td><td>${r.b_plus}</td><td>${r.b_minus}</td><td>${r.error}</td></tr>`).join('');
    } else {
        thead.innerHTML = `<tr>${encabezados.map(h => `<th>${h}</th>`).join('')}</tr>`;
        tbody.innerHTML = resultados.map(r => {
            if (r.is_sep) return `<tr class="separator-row"><td colspan="${encabezados.length}"></td></tr>`;
            return `<tr>${r.data.map(d => `<td>${d}</td>`).join('')}</tr>`;
        }).join('');
    }

    if (window.animarTabla) window.animarTabla('#tabla-pol');
}

function limpiarPol() {
    animarLimpieza(() => {
        document.getElementById('tol-pol').value = '';
        document.querySelectorAll('[id^="coef-"]').forEach(c => c.value = '');
        document.getElementById('thead-pol').innerHTML = '';
        document.getElementById('tbody-pol').innerHTML = '';
        document.getElementById('consola-pol').value = '';
        document.getElementById('btn-exportar-pol').disabled = true;
        actualizarCamposPol();
    });
}

// ─── Sistemas No Lineales ────────────────────────────────────────────────────

function generarCamposSistemas() {
    const n = parseInt(document.getElementById('n-sis')?.value || 2);
    const container = document.getElementById('container-sis');
    if (!container) return;
    
    container.innerHTML = Array.from({length: n}, (_, i) => i + 1).map(i => `
        <div class="system-eq-card" style="opacity: 0;">
            <div class="eq-row">
                <span class="eq-label">f_${i}:</span>
                <input type="text" id="sis-f-${i}" placeholder="f_${i}(x...) = 0" class="input-control" oninput="previewMath('sis-f-${i}', 'preview-sis-${i}')">
                <div id="preview-sis-${i}" class="math-preview" style="font-size: 0.85rem; min-height: 30px;"></div>
            </div>
            <div class="eq-row">
                <span class="eq-label alt">x_${i} init:</span>
                <input type="text" id="sis-x-${i}" class="input-control text-center">
            </div>
        </div>`).join('');

    if (window.anime) {
        anime({
            targets: '.system-eq-card',
            translateX: [-10, 0],
            opacity: [0, 1],
            delay: anime.stagger(100),
            duration: 600,
            easing: 'easeOutExpo'
        });
    }
}

async function calcularSis() {
    const n = parseInt(document.getElementById('n-sis')?.value || 2);
    const payload = {
        n,
        tol: document.getElementById('tol-sis')?.value,
        iter: document.getElementById('iter-sis')?.value,
        angulo: document.getElementById('angulo-sis')?.value || 'rad',
        funciones: [],
        x0: []
    };

    for (let i = 1; i <= n; i++) {
        payload.funciones.push(document.getElementById(`sis-f-${i}`).value);
        payload.x0.push(document.getElementById(`sis-x-${i}`).value);
    }

    if (Object.values(payload).some(v => v === "" || (Array.isArray(v) && v.some(x => x === "")))) {
        return showAlert('Atención', 'Complete todos los campos.', 'warning');
    }

    const data = await performRequest('/api/calcular_sis', payload, 'btn-calc-sis');
    
    if (data.consola) document.getElementById('consola-sis').value = data.consola;
    if (data.error) return showAlert('Error', data.error, 'error');
    
    document.getElementById('thead-sis').innerHTML = `<tr>${data.headers.map(h => `<th>${h}</th>`).join('')}</tr>`;
    document.getElementById('tbody-sis').innerHTML = data.resultados.map(row => `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`).join('');
    document.getElementById('btn-exportar-sis').disabled = false;

    if (n === 2) {
        graficarSis3D(payload.funciones);
    }

    if (window.animarTabla) window.animarTabla('#tabla-sis');
    playSound('success');
    salvarHistorial('Newton NR Multivariable', payload);
}

async function graficarSis3D(funciones) {
    const data = await performRequest('/api/grafica_sis_3d', { funciones });
    if (data.error) return;

    const section = document.getElementById('grafica-3d-seccion');
    if (section) section.style.display = 'block';

    const traces = data.Z.map((z, i) => ({
        z: z,
        x: data.X,
        y: data.Y,
        type: 'surface',
        name: `f_${i+1}`,
        opacity: 0.8,
        colorscale: i === 0 ? 'Viridis' : 'Hot'
    }));

    // Plano z=0
    traces.push({
        z: data.X.map(() => data.Y.map(() => 0)),
        x: data.X,
        y: data.Y,
        type: 'surface',
        opacity: 0.3,
        showscale: false,
        colorscale: [[0, 'gray'], [1, 'gray']]
    });

    Plotly.newPlot('plotly-3d', traces, {
        title: 'Superficies del Sistema',
        autosize: true,
        margin: { l: 0, r: 0, b: 0, t: 40 },
        scene: {
            xaxis: {title: 'x1'},
            yaxis: {title: 'x2'},
            zaxis: {title: 'f(x)'}
        },
        paper_bgcolor: 'transparent',
        font: { color: '#fff' }
    });
}

function limpiarSis() {
    animarLimpieza(() => {
        ['tol-sis', 'iter-sis'].forEach(id => document.getElementById(id).value = '');
        generarCamposSistemas();
        document.getElementById('thead-sis').innerHTML = '';
        document.getElementById('tbody-sis').innerHTML = '';
        document.getElementById('consola-sis').value = '';
        document.getElementById('btn-exportar-sis').disabled = true;
    });
}

/**
 * Sistema de Persistencia de Historial
 */
function salvarHistorial(metodo, payload) {
    let historial = JSON.parse(localStorage.getItem('historial_num') || '[]');
    const nuevo = {
        id: Date.now(),
        metodo,
        payload,
        fecha: new Date().toLocaleString()
    };
    
    if (historial.length > 0 && JSON.stringify(historial[0].payload) === JSON.stringify(payload)) return;

    historial.unshift(nuevo);
    if (historial.length > 10) historial.pop();
    localStorage.setItem('historial_num', JSON.stringify(historial));
}

// Inicializadores
document.addEventListener('DOMContentLoaded', () => {
    // Inits de vistas
    if (document.getElementById('metodo-nl')) actualizarCamposNL();
    if (document.getElementById('metodo-pol')) {
        actualizarCamposPol();
        generarCamposCoeficientes();
    }
    if (document.getElementById('n-sis')) generarCamposSistemas();
});
