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
 * Usa el HUD global (#math-hud) para no ocupar espacio en el formulario.
 * Apoya fórmulas con fracciones, exponentes, trig y logaritmos.
 */
let _mathPreviewTimer = null;

function previewMath(inputId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById('preview-' + inputId);
    if (!input || !preview) return;

    clearTimeout(_mathPreviewTimer);
    const text = input.value.trim();

    if (!text) {
        preview.classList.remove('active');
        return;
    }

    _mathPreviewTimer = setTimeout(() => {
        if (typeof math === 'undefined' || typeof katex === 'undefined') return;

        try {
            // Limpieza y estandarización para math.js
            let cleanText = text
                .replace(/\*\*/g, '^')
                .replace(/ln\(/g, 'log(')
                .replace(/log10\(/g, 'log10(');

            const node = math.parse(cleanText);
            let latex = node.toTex({ parenthesis: 'keep' });

            // Post-procesamiento para que KaTeX se vea mejor
            latex = latex
                .replace(/\\cdot/g, ' \\cdot ')
                .replace(/\\exp/g, 'e^{') 
                .replace(/e\^\{([^}]+)\}/g, (m, p1) => `e^{${p1}}`);

            preview.classList.add('active');
            katex.render(latex, preview, {
                throwOnError: false,
                displayMode: true
            });
        } catch (e) {
            // Fallback para cuando la expresión está incompleta
            preview.classList.add('active');
            preview.innerHTML = `<small style="opacity:0.5; font-size:0.7rem; letter-spacing:1px;">CONSTRUYENDO...</small>`;
        }
    }, 150);
}

function hideMathPreview() {
    document.querySelectorAll('.math-preview').forEach(p => p.classList.remove('active'));
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


// ─── Ecuaciones No Lineales ──────────────────────────────────────────────────

function actualizarCamposNL() {
    const metodo = document.getElementById('metodo-nl')?.value;
    const container = document.getElementById('campos-dinamicos-nl');
    const btnDespejar = document.getElementById('btn-despejar-x');
    const panelDespejes = document.getElementById('despejes-container');

    // Mostrar/ocultar botón de despeje
    if (btnDespejar) {
        btnDespejar.style.display = (metodo === 'Punto fijo') ? 'inline-block' : 'none';
    }
    // Ocultar panel de despejes si no es Punto Fijo
    if (panelDespejes && metodo !== 'Punto fijo') {
        panelDespejes.style.display = 'none';
    }

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
        hideMathPreview();
        const res = document.getElementById('resultado-nl');
        if (res) {
            res.textContent = 'Esperando parámetros...';
            res.className = 'resultado-tarjeta flex-3 text-center';
        }
        document.getElementById('btn-exportar-nl').disabled = true;
        if (document.getElementById('btn-pdf-nl')) document.getElementById('btn-pdf-nl').disabled = true;
        const panelDespejes = document.getElementById('despejes-container');
        if (panelDespejes) panelDespejes.style.display = 'none';
        actualizarCamposNL();
    });
}

/**
 * Obtiene despejes simbólicos para Punto Fijo
 */
async function obtenerDespejes() {
    const ecuacion = document.getElementById('ecuacion-nl')?.value;
    const x0 = document.getElementById('nl-x0')?.value;
    
    if (!ecuacion) return showAlert('Atención', 'Ingresa una ecuación f(x) primero.', 'warning');

    const container = document.getElementById('despejes-container');
    const list = document.getElementById('despejes-list');
    if (!container || !list) return;

    list.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--text-muted);">
            <i class="ph-bold ph-spinner-gap spin" style="font-size: 1.5rem; margin-bottom: 0.8rem; display: block; margin: 0 auto 0.8rem;"></i>
            Analizando posibilidades simbólicas y convergencia...
        </div>`;
    container.style.display = 'block';

    const data = await performRequest('/api/despejar_punto_fijo', { ecuacion, x0 }, 'btn-despejar-x');

    if (data.error) {
        list.innerHTML = `<div style="grid-column: 1/-1; color: var(--color-danger); text-align: center; padding: 1rem;">${data.error}</div>`;
        return;
    }

    if (!data.despejes || data.despejes.length === 0) {
        list.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 1rem;">No se encontraron despejes automáticos útiles. Prueba una ecuación más simple o despéjala manualmente.</div>`;
        return;
    }

    list.innerHTML = '';
    data.despejes.forEach((d, index) => {
        const card = document.createElement('div');
        card.className = `despeje-card ${d.converge ? 'convergent' : (d.eval !== null ? 'divergent' : '')}`;
        
        const badge = d.converge ? '<span class="conv-badge success">Converge</span>' : 
                      d.eval !== null ? '<span class="conv-badge error">Diverge</span>' : '';
                      
        const evalHtml = d.eval !== null ? `
            <div class="despeje-step-title">PASO 3: Evaluación Numérica ($x_0$)</div>
            <div class="despeje-eval">|g'(${x0})| ≈ ${d.eval.toFixed(6)}</div>
            <div class="despeje-step-title">PASO 4: Criterio y Conclusión</div>
            <div class="despeje-conclusion">${d.converge ? 'EL MÉTODO CONVERGE' : 'EL MÉTODO DIVERGE'}</div>
        ` : '';

        card.innerHTML = `
            ${badge}
            <div class="despeje-index">g<sub>${index + 1}</sub>(x)</div>
            
            <div class="despeje-step-title">PASO 1: Despeje Natural</div>
            <div class="despeje-math"></div>
            
            <div class="despeje-step-title">PASO 2: Derivada Compacta</div>
            <div class="despeje-deriv-math"></div>
            
            ${evalHtml}
            
            <div class="despeje-action">Seleccionar esta función</div>
        `;
        
        card.onclick = () => {
            document.getElementById('ecuacion-nl').value = d.expr;
            previewMath('ecuacion-nl');
            showAlert('Función Seleccionada', `Se ha cargado g${index+1}(x) como función de iteración.`, 'success');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        };
        
        list.appendChild(card);
        
        if (window.katex) {
            const mathEl = card.querySelector('.despeje-math');
            const derivEl = card.querySelector('.despeje-deriv-math');
            window.katex.render(`x = ${d.latex}`, mathEl, { throwOnError: false, displayMode: true });
            window.katex.render(`g'_{${index+1}}(x) = ${d.derivada}`, derivEl, { throwOnError: false, displayMode: true });
        }
    });

    if (window.anime) {
        window.anime({
            targets: '.despeje-card',
            translateY: [20, 0],
            opacity: [0, 1],
            delay: window.anime.stagger(80),
            duration: 600,
            easing: 'easeOutQuart'
        });
    }
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
            <div class="eq-row input-group">
                <span class="eq-label">f_${i}:</span>
                <input type="text" id="sis-f-${i}" placeholder="f_${i}(x...) = 0" class="input-control" oninput="previewMath('sis-f-${i}')">
                <div class="math-preview" id="preview-sis-f-${i}"></div>
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
    try {
        const nInput = document.getElementById('n-sis');
        if (!nInput) return;
        const n = parseInt(nInput.value || 2);
        
        const payload = {
            n,
            tol: document.getElementById('tol-sis')?.value,
            iter: document.getElementById('iter-sis')?.value,
            angulo: document.getElementById('angulo-sis')?.value || 'rad',
            funciones: [],
            x0: []
        };

        for (let i = 1; i <= n; i++) {
            const fEl = document.getElementById(`sis-f-${i}`);
            const xEl = document.getElementById(`sis-x-${i}`);
            if (fEl && xEl) {
                payload.funciones.push(fEl.value);
                payload.x0.push(xEl.value);
            }
        }

        if (payload.funciones.length < n || !payload.tol || !payload.iter || payload.funciones.some(f => !f) || payload.x0.some(x => !x)) {
            return showAlert('Atención', 'Complete todos los campos.', 'warning');
        }

        console.log("[DEBUG JS] Enviando petición a /api/calcular_sis:", payload);
        const data = await performRequest('/api/calcular_sis', payload, 'btn-calc-sis');
        console.log("[DEBUG JS] Respuesta recibida:", data);
        
        if (data.consola) document.getElementById('consola-sis').value = data.consola;
        if (data.error) return showAlert('Error', data.error, 'error');
        
        document.getElementById('thead-sis').innerHTML = `<tr>${data.headers.map(h => `<th>${h}</th>`).join('')}</tr>`;
        document.getElementById('tbody-sis').innerHTML = data.resultados.map(row => `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`).join('');
        document.getElementById('btn-exportar-sis').disabled = false;

        console.log("[DEBUG JS] data.raiz:", data.raiz, "| n:", n);

        // Obtener la solución: primero de data.raiz, si no de la última fila de la tabla
        let raiz = data.raiz;
        if (!raiz && data.resultados && data.resultados.length > 0) {
            const lastRow = data.resultados[data.resultados.length - 1];
            // Las columnas son: [iter, x1, x2, ...xn, error]
            raiz = lastRow.slice(1, n + 1).map(v => parseFloat(v));
            console.log("[DEBUG JS] Raíz extraída de resultados:", raiz);
        }

        if (raiz && n >= 2) {
            // Extraer trayectoria de iteraciones de la tabla de resultados
            const trayectoria = (data.resultados || []).map(row => ({
                x: parseFloat(row[1]),
                y: parseFloat(row[2]),
                z: n >= 3 ? parseFloat(row[3]) : 0
            })).filter(p => !isNaN(p.x) && !isNaN(p.y));

            // Actualizar labels del panel
            const lbl  = document.getElementById('label-grafica-3d');
            const desc = document.getElementById('desc-grafica-3d');
            if (lbl)  lbl.textContent  = n === 2 ? 'Visualización 3D del Sistema (n=2):' :
                                          n === 3 ? 'Visualización 3D del Sistema (n=3):' :
                                                    `Visualización 3D del Sistema (n=${n}, proyección):`;
            if (desc) desc.textContent = n === 2
                ? 'Las superficies f₁(x,y) y f₂(x,y) se cruzan donde f=0. La línea punteada muestra la convergencia.'
                : n === 3
                ? 'Isosuperficies f=0 de las 3 ecuaciones. Su intersección (verde) es la solución del sistema.'
                : 'Se muestran f₁ y f₂ fijando las variables adicionales en su valor solución.';

            // Guardar contexto para re-ploteo (selector de variables, n>3)
            window._sis3d_ctx = { funciones: payload.funciones, raiz, n, trayectoria, var_names: data.var_names || [] };
            if (n > 3) mostrarSelectorVariables(data.var_names || [], raiz);

            graficarSis3D(payload.funciones, raiz, n, trayectoria);
        }

        if (window.animarTabla) window.animarTabla('#tabla-sis');
        playSound('success');
        salvarHistorial('Newton NR Multivariable', payload);
    } catch (err) {
        console.error("[CRITICAL JS ERROR]", err);
        showAlert('Error Crítico', 'Error en el navegador: ' + err.message, 'error');
    }
}

async function graficarSis3D(funciones, x_sol = null, n = 2, trayectoria = []) {
    const OLIVE_GREEN  = '#6B8E23';
    const LIME_GREEN   = '#84cc16';
    const START_COLOR  = '#f97316'; // orange for start point
    const PATH_COLOR   = '#facc15'; // yellow for path

    const section   = document.getElementById('grafica-3d-seccion');
    const container = document.getElementById('plotly-3d');
    if (!section || !container) return;

    section.style.display = 'block';
    container.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;height:520px;color:#94a3b8;gap:12px;">
        <i class="ph-bold ph-spinner-gap spin" style="font-size:1.5rem;"></i>
        <span>Calculando superficies ${n >= 3 ? 'volumétricas' : '3D'}…</span>
    </div>`;

    try {
        // Determinar variables de ejes según selector (n>3) o automático
        const selX = document.getElementById('sel-var-x');
        const selY = document.getElementById('sel-var-y');
        const selZ = document.getElementById('sel-var-z');

        const payload = {
            funciones, x_sol, n,
            var_x: selX ? selX.value : null,
            var_y: selY ? selY.value : null,
            var_z: selZ ? selZ.value : null
        };

        // Variables fijadas para n>3
        if (n > 3 && window._sis3d_ctx) {
            const ctx = window._sis3d_ctx;
            const usedVars = [payload.var_x, payload.var_y, payload.var_z].filter(Boolean);
            const fixedVars = {};
            ctx.var_names.forEach((vn, idx) => {
                if (!usedVars.includes(vn) && idx < ctx.raiz.length) {
                    fixedVars[vn] = ctx.raiz[idx];
                }
            });
            payload.fixed_vars   = fixedVars;
            payload.var_names    = ctx.var_names;
        }

        const response = await fetch('/api/grafica_sis_3d', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();

        if (data.error) {
            container.innerHTML = `<div style="color:#ef4444;padding:2rem;">⚠ ${data.error}</div>`;
            return;
        }

        const sym = data.simbolos || ['x', 'y', 'z'];
        const traces = [];

        // ─── MODO 2D (n=2): Superficies f(x,y)=Z ─────────────────────────────
        if (data.mode === '2d') {
            const palettes = ['Viridis', 'Electric'];
            data.Z.forEach((zMatrix, i) => {
                traces.push({
                    type: 'surface', name: `f<sub>${i+1}</sub>`,
                    x: data.X, y: data.Y, z: zMatrix,
                    opacity: 0.75, showscale: false,
                    colorscale: palettes[i] || 'Cividis',
                    contours: { z: { show: true, usecolormap: true, highlightcolor: '#fff', project: { z: false } } }
                });
            });

            // Plano z=0 (intersección)
            traces.push({
                type: 'surface', name: 'f=0',
                x: data.X, y: data.Y,
                z: data.X.map(() => data.Y.map(() => 0)),
                opacity: 0.15, showscale: false,
                colorscale: [[0, 'rgba(255,255,255,0.05)'], [1, 'rgba(255,255,255,0.05)']]
            });

            // Raíz en z=0
            if (x_sol) {
                traces.push({
                    type: 'scatter3d', name: 'Solución', mode: 'markers',
                    x: [parseFloat(x_sol[0])], y: [parseFloat(x_sol[1])], z: [0],
                    marker: { size: 14, color: OLIVE_GREEN, symbol: 'diamond',
                              line: { color: LIME_GREEN, width: 3 } }
                });
            }

            // Trayectoria de iteraciones en z=0
            if (trayectoria.length > 1) {
                traces.push({
                    type: 'scatter3d', name: 'Convergencia', mode: 'lines+markers',
                    x: trayectoria.map(p => p.x),
                    y: trayectoria.map(p => p.y),
                    z: trayectoria.map(() => 0),
                    line:   { color: PATH_COLOR, width: 5, dash: 'dot' },
                    marker: { size: 5, color: PATH_COLOR }
                });
                // Punto inicial
                traces.push({
                    type: 'scatter3d', name: 'x₀', mode: 'markers',
                    x: [trayectoria[0].x], y: [trayectoria[0].y], z: [0],
                    marker: { size: 10, color: START_COLOR, symbol: 'square',
                              line: { color: 'white', width: 2 } }
                });
            }

        // ─── MODO 3D (n>=3): Isosuperficies f(x,y,z)=0 ──────────────────────
        } else if (data.mode === '3d') {
            const isoColors = ['Viridis', 'Electric', 'Hot'];
            const isoOpacity = [0.35, 0.30, 0.28];

            data.values.forEach((vals, i) => {
                traces.push({
                    type: 'isosurface', name: `f<sub>${i+1}</sub>=0`,
                    x: data.x_flat, y: data.y_flat, z: data.z_flat,
                    value: vals,
                    isomin: -0.5, isomax: 0.5,
                    surface: { count: 1, fill: 1 },
                    opacity: isoOpacity[i] || 0.3,
                    colorscale: isoColors[i] || 'Cividis',
                    showscale: false,
                    caps: { x: { show: false }, y: { show: false }, z: { show: false } }
                });
            });

            // Punto solución (3D)
            if (x_sol && x_sol.length >= 3) {
                traces.push({
                    type: 'scatter3d', name: 'Solución', mode: 'markers',
                    x: [parseFloat(x_sol[0])],
                    y: [parseFloat(x_sol[1])],
                    z: [parseFloat(x_sol[2])],
                    marker: { size: 14, color: OLIVE_GREEN, symbol: 'diamond',
                              line: { color: LIME_GREEN, width: 4 } }
                });
            }

            // Trayectoria 3D real
            if (trayectoria.length > 1) {
                traces.push({
                    type: 'scatter3d', name: 'Convergencia', mode: 'lines+markers',
                    x: trayectoria.map(p => p.x),
                    y: trayectoria.map(p => p.y),
                    z: trayectoria.map(p => p.z),
                    line:   { color: PATH_COLOR, width: 6, dash: 'dot' },
                    marker: { size: 4, color: PATH_COLOR }
                });
                traces.push({
                    type: 'scatter3d', name: 'x₀', mode: 'markers',
                    x: [trayectoria[0].x], y: [trayectoria[0].y], z: [trayectoria[0].z],
                    marker: { size: 11, color: START_COLOR, symbol: 'square',
                              line: { color: 'white', width: 2 } }
                });
            }
        }

        // ─── Layout: Dark + Glassmorphism + Olive Accents ─────────────────────
        const gridStyle = { gridcolor: '#334155', zerolinecolor: '#475569', color: '#94a3b8' };
        const layout = {
            autosize: true, height: 560,
            margin: { l: 0, r: 0, b: 0, t: 0 },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor:  'rgba(0,0,0,0)',
            font: { family: "'Inter', sans-serif", color: '#cbd5e1', size: 12 },
            showlegend: true,
            legend: {
                bgcolor: 'rgba(15,23,42,0.75)', bordercolor: '#334155', borderwidth: 1,
                font: { color: '#e2e8f0', size: 11 }, x: 0.01, y: 0.99
            },
            scene: {
                bgcolor: 'rgba(2,6,23,0.6)',
                xaxis: { title: { text: sym[0] || 'X', font: { color: LIME_GREEN } }, ...gridStyle },
                yaxis: { title: { text: sym[1] || 'Y', font: { color: LIME_GREEN } }, ...gridStyle },
                zaxis: { title: { text: sym[2] || (data.mode === '2d' ? 'f(x,y)' : 'Z'), font: { color: LIME_GREEN } }, ...gridStyle },
                camera: { eye: { x: 1.6, y: 1.6, z: 1.2 } }
            }
        };

        Plotly.newPlot(container, traces, layout, { responsive: true, displayModeBar: true });
        setTimeout(() => Plotly.Plots.resize(container), 120);

    } catch (err) {
        console.error('[3D ERROR]', err);
        container.innerHTML = `<div style="color:#ef4444;padding:2rem;">⚠ Error: ${err.message}</div>`;
    }
}

/** Muestra panel selector de variables para n>3 */
function mostrarSelectorVariables(var_names, raiz) {
    let panel = document.getElementById('panel-var-selector');
    if (!panel) return;
    panel.style.display = 'block';
    const opciones = var_names.map(v => `<option value="${v}">${v}</option>`).join('');
    document.getElementById('sel-var-x').innerHTML = opciones;
    document.getElementById('sel-var-y').innerHTML = opciones;
    document.getElementById('sel-var-z').innerHTML = opciones;
    // Selección por defecto: primeras 3
    if (var_names.length > 0) document.getElementById('sel-var-x').value = var_names[0];
    if (var_names.length > 1) document.getElementById('sel-var-y').value = var_names[1];
    if (var_names.length > 2) document.getElementById('sel-var-z').value = var_names[2];
}

/** Re-graficar desde el panel selector (n>3) */
function regraficar3D() {
    const ctx = window._sis3d_ctx;
    if (!ctx) return;
    graficarSis3D(ctx.funciones, ctx.raiz, ctx.n, ctx.trayectoria);
}


function limpiarSis() {
    animarLimpieza(() => {
        ['tol-sis', 'iter-sis'].forEach(id => document.getElementById(id).value = '');
        generarCamposSistemas();
        document.getElementById('thead-sis').innerHTML = '';
        document.getElementById('tbody-sis').innerHTML = '';
        const section = document.getElementById('grafica-3d-seccion');
        if (section) section.style.display = 'none';
        
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
