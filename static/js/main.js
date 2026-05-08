// Utilidad para notificaciones
function showAlert(title, text, icon) {
    Swal.fire({
        title: title,
        text: text,
        icon: icon,
        background: '#1e293b',
        color: '#f8fafc',
        confirmButtonColor: '#6366f1'
    });
}

// Exportar tabla a Excel
function exportarExcel(tablaId, nombreArchivo) {
    let table = document.getElementById(tablaId);
    let rows = table.querySelectorAll('tr');
    let csv = [];
    
    for (let i = 0; i < rows.length; i++) {
        let row = [], cols = rows[i].querySelectorAll('td, th');
        
        for (let j = 0; j < cols.length; j++) {
            let data = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, '').replace(/(\s\s)/gm, ' ');
            data = data.replace(/"/g, '""');
            row.push('"' + data + '"');
        }
        if(row.length > 0) csv.push(row.join(','));
    }
    
    let csvString = csv.join('\n');
    let blob = new Blob(["\ufeff", csvString], { type: 'text/csv;charset=utf-8;' });
    let link = document.createElement("a");
    if (link.download !== undefined) {
        let url = URL.createObjectURL(blob);
        link.setAttribute("href", url);
        link.setAttribute("download", nombreArchivo + ".csv");
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// =========================================================================
// ECUACIONES NO LINEALES
// =========================================================================
function actualizarCamposNL() {
    const metodo = document.getElementById('metodo-nl');
    if (!metodo) return;
    
    const container = document.getElementById('campos-dinamicos-nl');
    container.innerHTML = '';
    
    const val = metodo.value;
    
    if (val === 'Bisección' || val === 'Regla Falsa') {
        container.innerHTML = `
            <div class="input-group flex-1">
                <label>Límite Inferior (a):</label>
                <input type="text" id="nl-a" class="input-control">
            </div>
            <div class="input-group flex-1">
                <label>Límite Superior (b):</label>
                <input type="text" id="nl-b" class="input-control">
            </div>
        `;
    } else if (val === 'Newton-Raphson') {
        container.innerHTML = `
            <div class="input-group flex-1">
                <label>Punto inicial (ci):</label>
                <input type="text" id="nl-ci" class="input-control">
            </div>
        `;
    } else if (val === 'Secante') {
        container.innerHTML = `
            <div class="input-group flex-1">
                <label>Primer punto (x0):</label>
                <input type="text" id="nl-x0" class="input-control">
            </div>
            <div class="input-group flex-1">
                <label>Segundo punto (x1):</label>
                <input type="text" id="nl-x1" class="input-control">
            </div>
        `;
    } else if (val === 'Punto fijo') {
        container.innerHTML = `
            <div class="input-group flex-1">
                <label>Punto inicial (x0):</label>
                <input type="text" id="nl-x0" class="input-control">
            </div>
        `;
    }
}

async function calcularNL(force = false) {
    const ecuacion = document.getElementById('ecuacion-nl').value;
    const metodo = document.getElementById('metodo-nl').value;
    const tol = document.getElementById('tol-nl').value;
    const angulo = document.getElementById('angulo-nl') ? document.getElementById('angulo-nl').value : 'rad';
    
    if (!ecuacion || !tol) {
        return showAlert('Atención', 'Ingresa una ecuación y la tolerancia.', 'warning');
    }

    const payload = { ecuacion, metodo, tol, angulo, force };
    
    if (metodo === 'Bisección' || metodo === 'Regla Falsa') {
        payload.a = document.getElementById('nl-a').value;
        payload.b = document.getElementById('nl-b').value;
        if (!payload.a || !payload.b) return showAlert('Atención', 'Llene a y b.', 'warning');
    } else if (metodo === 'Newton-Raphson') {
        payload.ci = document.getElementById('nl-ci').value;
        if (!payload.ci) return showAlert('Atención', 'Llene ci.', 'warning');
    } else if (metodo === 'Secante') {
        payload.x0 = document.getElementById('nl-x0').value;
        payload.x1 = document.getElementById('nl-x1').value;
        if (!payload.x0 || !payload.x1) return showAlert('Atención', 'Llene x0 y x1.', 'warning');
    } else if (metodo === 'Punto fijo') {
        payload.x0 = document.getElementById('nl-x0').value;
        if (!payload.x0) return showAlert('Atención', 'Llene x0.', 'warning');
    }

    const res = await fetch('/api/calcular_nl', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    
    const data = await res.json();
    
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
        }).then((result) => {
            if (result.isConfirmed) {
                calcularNL(true);
            }
        });
        return;
    }
    
    if (data.error) {
        return showAlert('Error', data.error, 'error');
    }
    
    // Guardar datos para la gráfica
    window._lastResultadosNL = data.resultados;
    window._lastMetodoNL     = metodo;
    window._lastRaiz         = data.mensaje;
    
    renderTablaNL(data.resultados, metodo);
    const resultDiv = document.getElementById('resultado-nl');
    resultDiv.textContent = data.mensaje;
    resultDiv.className = 'resultado-tarjeta flex-3 text-center success';
    document.getElementById('btn-exportar-nl').disabled = false;
}

function renderTablaNL(resultados, metodo) {
    const thead = document.getElementById('thead-nl');
    const tbody = document.getElementById('tbody-nl');
    
    if (metodo === 'Bisección' || metodo === 'Regla Falsa') {
        thead.innerHTML = `<th>It</th><th>a</th><th>b</th><th>c</th><th>f(a)</th><th>f(b)</th><th>f(c)</th><th>f(a)*f(c)</th><th>Er%</th>`;
        tbody.innerHTML = resultados.map(r => `<tr><td>${r.iter}</td><td>${r.a}</td><td>${r.b}</td><td>${r.c}</td><td>${r.fa}</td><td>${r.fb}</td><td>${r.fc}</td><td>${r.prueba}</td><td>${r.error}</td></tr>`).join('');
    } else if (metodo === 'Newton-Raphson') {
        thead.innerHTML = `<th>It</th><th>ci</th><th>f(ci)</th><th>f'(ci)</th><th>ci+1</th><th>Er%</th>`;
        tbody.innerHTML = resultados.map(r => `<tr><td>${r.iter}</td><td>${r.ci}</td><td>${r.fci}</td><td>${r.dfci}</td><td>${r.cimas1}</td><td>${r.error}</td></tr>`).join('');
    } else if (metodo === 'Secante') {
        thead.innerHTML = `<th>It</th><th>Ci</th><th>f(ci)</th><th>Er%</th>`;
        tbody.innerHTML = resultados.map(r => `<tr><td>${r.iter}</td><td>${r.ci}</td><td>${r.fci}</td><td>${r.error}</td></tr>`).join('');
    } else if (metodo === 'Punto fijo') {
        thead.innerHTML = `<th>It</th><th>Ci</th><th>g(Ci)</th><th>Er%</th>`;
        tbody.innerHTML = resultados.map(r => `<tr><td>${r.iter}</td><td>${r.ci}</td><td>${r.gci}</td><td>${r.error}</td></tr>`).join('');
    }

    // Animación de fluidez para la tabla
    if (window.animarTabla) window.animarTabla('#tabla-nl');
}

function limpiarNL() {
    animarLimpieza(() => {
        document.getElementById('ecuacion-nl').value = '';
        document.getElementById('tol-nl').value = '';
        document.getElementById('thead-nl').innerHTML = '';
        document.getElementById('tbody-nl').innerHTML = '';
        const res = document.getElementById('resultado-nl');
        res.textContent = 'Esperando parámetros...';
        res.className = 'resultado-tarjeta flex-3 text-center';
        document.getElementById('btn-exportar-nl').disabled = true;
        actualizarCamposNL();
    });
}

// =========================================================================
// POLINOMIOS
// =========================================================================
function generarCamposCoeficientes() {
    const gradoElem = document.getElementById('grado-pol');
    if (!gradoElem) return;
    const grado = parseInt(gradoElem.value);
    const container = document.getElementById('container-coefs');
    container.innerHTML = '';
    
    for (let i = grado; i >= 0; i--) {
        container.innerHTML += `
            <div class="input-group" style="opacity: 0;">
                <label style="color: var(--accent-blue); font-weight: 600; font-family: 'Fira Code', monospace;">a_${i}</label>
                <input type="text" id="coef-${i}" class="input-control text-center">
            </div>
        `;
    }

    // Animación fluida de aparición
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
    const metodo = document.getElementById('metodo-pol');
    if (!metodo) return;
    const container = document.getElementById('campos-dinamicos-pol');
    const seccionCoefs = document.getElementById('seccion-coeficientes');
    const grupoGrado = document.getElementById('grupo-grado');
    const grupoEq = document.getElementById('grupo-ecuacion-pol');
    container.innerHTML = '';
    
    if (metodo.value === 'Müller') {
        if(seccionCoefs) seccionCoefs.style.display = 'none';
        if(grupoGrado) grupoGrado.style.display = 'none';
        if(grupoEq) grupoEq.style.display = 'flex';
        
        container.innerHTML = `
            <div class="input-group flex-1"><label>x0:</label><input type="text" id="pol-x0" class="input-control"></div>
            <div class="input-group flex-1"><label>x1:</label><input type="text" id="pol-x1" class="input-control"></div>
            <div class="input-group flex-1"><label>x2:</label><input type="text" id="pol-x2" class="input-control"></div>
        `;
    } else {
        if(seccionCoefs) seccionCoefs.style.display = 'block';
        if(grupoGrado) grupoGrado.style.display = 'flex';
        if(grupoEq) grupoEq.style.display = 'none';
        
        if (metodo.value === 'Horner-Newton') {
            container.innerHTML = `
                <div class="input-group flex-1"><label>Valor inicial (r0):</label><input type="text" id="pol-r0" class="input-control"></div>
            `;
        } else if (metodo.value === 'Bairstow') {
            container.innerHTML = `
                <div class="input-group flex-1"><label>r0 (opcional):</label><input type="text" id="pol-r0-bair" class="input-control" placeholder="Automático"></div>
                <div class="input-group flex-1"><label>s0 (opcional):</label><input type="text" id="pol-s0-bair" class="input-control" placeholder="Automático"></div>
            `;
        }
    }
}

async function calcularPol() {
    const metodo = document.getElementById('metodo-pol').value;
    const tol = document.getElementById('tol-pol').value;
    
    const payload = { metodo, tol };
    
    if (metodo === 'Müller') {
        const ecuacion = document.getElementById('ecuacion-pol').value;
        if (!ecuacion) return showAlert('Atención', 'Ingresa una ecuación.', 'warning');
        payload.ecuacion = ecuacion;
        payload.x0 = document.getElementById('pol-x0').value;
        payload.x1 = document.getElementById('pol-x1').value;
        payload.x2 = document.getElementById('pol-x2').value;
        if(!payload.x0 || !payload.x1 || !payload.x2) return showAlert('Atención', 'Llene x0, x1 y x2', 'warning');
    } else {
        const grado = parseInt(document.getElementById('grado-pol').value);
        const coeficientes = [];
        for (let i = grado; i >= 0; i--) {
            const val = document.getElementById(`coef-${i}`).value;
            if (val === '') return showAlert('Atención', `Llene el coeficiente a_${i}`, 'warning');
            try {
                coeficientes.push(math.evaluate(val));
            } catch(e) {
                return showAlert('Error', `Sintaxis inválida en a_${i}`, 'error');
            }
        }
        payload.coeficientes = coeficientes;
        
        if (metodo === 'Horner-Newton') {
            payload.r0 = document.getElementById('pol-r0').value;
            if(!payload.r0) return showAlert('Atención', 'Llene r0', 'warning');
        } else if (metodo === 'Bairstow') {
            const r0_bair = document.getElementById('pol-r0-bair');
            const s0_bair = document.getElementById('pol-s0-bair');
            if (r0_bair && r0_bair.value !== '') payload.r0 = r0_bair.value;
            if (s0_bair && s0_bair.value !== '') payload.s0 = s0_bair.value;
        }
    }
    
    const res = await fetch('/api/calcular_pol', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    
    const data = await res.json();
    
    if (data.consola) document.getElementById('consola-pol').value = data.consola;
    if (data.error) return showAlert('Error', data.error, 'error');
    
    if (metodo === 'Bairstow') {
        const r0_input = document.getElementById('pol-r0-bair');
        const s0_input = document.getElementById('pol-s0-bair');
        if (r0_input && data.r_init !== undefined) r0_input.value = data.r_init.toFixed(4);
        if (s0_input && data.s_init !== undefined) s0_input.value = data.s_init.toFixed(4);
    }
    
    renderTablaPol(data.resultados, metodo, data.encabezados);
    document.getElementById('btn-exportar-pol').disabled = false;
}

function renderTablaPol(resultados, metodo, encabezados) {
    const thead = document.getElementById('thead-pol');
    const tbody = document.getElementById('tbody-pol');
    
    if (metodo === 'Müller') {
        thead.innerHTML = `<tr><th>i</th><th>X_i</th><th>X_{i+1}</th><th>h_i</th><th>h_{i+1}</th><th>f(X_i)</th><th>f(X_{i+1})</th><th>δ_i</th><th>δ_{i+1}</th><th>a</th><th>b</th><th>c</th><th>b+√</th><th>b-√</th><th>Error %</th><th>Continuar</th></tr>`;
        tbody.innerHTML = resultados.map(r => `<tr><td>${r.iter}</td><td>${r.x1}</td><td>${r.x2}</td><td>${r.h0}</td><td>${r.h1}</td><td>${r.f1}</td><td>${r.f2}</td><td>${r.d0}</td><td>${r.d1}</td><td>${r.a}</td><td>${r.b}</td><td>${r.c}</td><td>${r.b_plus}</td><td>${r.b_minus}</td><td>${r.error}</td><td>${r.condicion}</td></tr>`).join('');
    } else if (metodo === 'Bairstow') {
        thead.innerHTML = `<tr>${encabezados.map(h => `<th>${h}</th>`).join('')}</tr>`;
        tbody.innerHTML = resultados.map(r => {
            if (r.is_sep) return `<tr class="separator-row"><td colspan="${encabezados.length}"></td></tr>`;
            return `<tr>${r.data.map(d => `<td>${d}</td>`).join('')}</tr>`;
        }).join('');
    } else if (metodo === 'Horner-Newton') {
        thead.innerHTML = `<tr>${encabezados.map(h => `<th>${h}</th>`).join('')}</tr>`;
        tbody.innerHTML = resultados.map(r => `<tr>${r.data.map(d => `<td>${d}</td>`).join('')}</tr>`).join('');
    }

    // Animación de fluidez para la tabla
    if (window.animarTabla) window.animarTabla('#tabla-pol');
}

function limpiarPol() {
    animarLimpieza(() => {
        document.getElementById('tol-pol').value = '';
        if (document.getElementById('ecuacion-pol')) document.getElementById('ecuacion-pol').value = '';
        const coefs = document.querySelectorAll('[id^="coef-"]');
        coefs.forEach(c => c.value = '');
        document.getElementById('thead-pol').innerHTML = '';
        document.getElementById('tbody-pol').innerHTML = '';
        document.getElementById('consola-pol').value = '';
        document.getElementById('btn-exportar-pol').disabled = true;
        actualizarCamposPol();
    });
}

// =========================================================================
// SISTEMAS NO LINEALES
// =========================================================================
function generarCamposSistemas() {
    const nElem = document.getElementById('n-sis');
    if (!nElem) return;
    const n = parseInt(nElem.value);
    const container = document.getElementById('container-sis');
    container.innerHTML = '';
    
    for (let i = 1; i <= n; i++) {
        container.innerHTML += `
            <div class="system-eq-card" style="opacity: 0;">
                <div class="eq-row">
                    <span class="eq-label">f_${i}:</span>
                    <input type="text" id="sis-f-${i}" placeholder="Ecuación ${i} = 0" class="input-control">
                </div>
                <div class="eq-row">
                    <span class="eq-label alt">x_${i}:</span>
                    <input type="text" id="sis-x-${i}" placeholder="Valor inicial" class="input-control text-center">
                </div>
            </div>
        `;
    }

    // Animación fluida de aparición
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
    const n = parseInt(document.getElementById('n-sis').value);
    const tol = document.getElementById('tol-sis').value;
    const iter = document.getElementById('iter-sis').value;
    
    const funciones = [];
    const x0 = [];
    
    for (let i = 1; i <= n; i++) {
        funciones.push(document.getElementById(`sis-f-${i}`).value);
        x0.push(document.getElementById(`sis-x-${i}`).value);
    }
    
    const angulo = document.getElementById('angulo-sis') ? document.getElementById('angulo-sis').value : 'rad';
    const payload = { n, funciones, x0, tol, iter, angulo };
    
    const res = await fetch('/api/calcular_sis', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    
    const data = await res.json();
    
    if (data.consola) document.getElementById('consola-sis').value = data.consola;
    if (data.error) return showAlert('Error', data.error, 'error');
    
    const thead = document.getElementById('thead-sis');
    thead.innerHTML = `<tr>${data.headers.map(h => `<th>${h}</th>`).join('')}</tr>`;
    
    const tbody = document.getElementById('tbody-sis');
    tbody.innerHTML = data.resultados.map(row => `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`).join('');
    
    document.getElementById('btn-exportar-sis').disabled = false;

    // Animación de fluidez para la tabla
    if (window.animarTabla) window.animarTabla('#tabla-sis');
}

function limpiarSis() {
    animarLimpieza(() => {
        document.getElementById('tol-sis').value = '';
        document.getElementById('iter-sis').value = '';
        const n = parseInt(document.getElementById('n-sis').value);
        for (let i = 1; i <= n; i++) {
            document.getElementById(`sis-f-${i}`).value = '';
            document.getElementById(`sis-x-${i}`).value = '';
        }
        document.getElementById('thead-sis').innerHTML = '';
        document.getElementById('tbody-sis').innerHTML = '';
        document.getElementById('consola-sis').value = '';
        document.getElementById('btn-exportar-sis').disabled = true;
    });
}

// Inicializadores
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('metodo-nl')) actualizarCamposNL();
    if (document.getElementById('metodo-pol')) {
        actualizarCamposPol();
        generarCamposCoeficientes();
    }
    if (document.getElementById('n-sis')) generarCamposSistemas();
});
