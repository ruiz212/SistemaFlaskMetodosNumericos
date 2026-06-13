document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('integracion-form');
    const btnSimple = document.getElementById('btn-simple');
    const btnDoble = document.getElementById('btn-doble');
    const tipoIntegralInput = document.getElementById('tipo_integral');
    const seccionDoble = document.getElementById('seccion-doble');
    
    const labelLimitesX = document.getElementById('label-limites-x');
    const labelNx = document.getElementById('label-n-x');
    
    const btnLimpiar = document.getElementById('btn-limpiar');
    
    // Toggle Simple/Doble
    btnSimple.addEventListener('click', (e) => {
        e.preventDefault();
        tipoIntegralInput.value = 'simple';
        
        btnSimple.className = 'btn btn-primary flex-1';
        btnSimple.style.background = '';
        
        btnDoble.className = 'btn flex-1';
        btnDoble.style.background = 'var(--bg-input)';
        
        seccionDoble.style.display = 'none';
        
        labelLimitesX.textContent = 'Límites de Integración';
        labelNx.textContent = 'Subdivisiones (n)';
        
        document.getElementById('c_val').removeAttribute('required');
        document.getElementById('d_val').removeAttribute('required');
        document.getElementById('m_val').removeAttribute('required');
        
        document.getElementById('funcion-hint').textContent = "Usa 'x' como variable. Ejemplo: sin(x) + e^x";
    });

    btnDoble.addEventListener('click', (e) => {
        e.preventDefault();
        tipoIntegralInput.value = 'doble';
        
        btnDoble.className = 'btn btn-primary flex-1';
        btnDoble.style.background = '';
        
        btnSimple.className = 'btn flex-1';
        btnSimple.style.background = 'var(--bg-input)';
        
        seccionDoble.style.display = 'block';
        
        labelLimitesX.textContent = 'Límites de Integración X';
        labelNx.textContent = 'Subdivisiones (nx)';
        
        document.getElementById('c_val').setAttribute('required', 'required');
        document.getElementById('d_val').setAttribute('required', 'required');
        document.getElementById('m_val').setAttribute('required', 'required');
        
        document.getElementById('funcion-hint').textContent = "Usa 'x' e 'y' como variables. Ejemplo: x^2 + y^2";
    });

    const metodoSelect = document.getElementById('metodo');
    const bgMethodName = document.getElementById('bg-method-name');

    metodoSelect.addEventListener('change', () => {
        bgMethodName.textContent = metodoSelect.options[metodoSelect.selectedIndex].text;
    });

    btnLimpiar.addEventListener('click', () => {
        form.reset();
        document.getElementById('resultado-integracion-container').style.display = 'none';
        document.getElementById('resultado-final').innerHTML = '';
        document.getElementById('consola-salida').value = '';
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const data = {
            ecuacion: document.getElementById('ecuacion').value,
            metodo: document.getElementById('metodo').value,
            tipo: document.getElementById('tipo_integral').value,
            a: document.getElementById('a_val').value,
            b: document.getElementById('b_val').value,
            n: document.getElementById('n_val').value
        };
        
        if (data.tipo === 'doble') {
            data.c = document.getElementById('c_val').value;
            data.d = document.getElementById('d_val').value;
            data.m = document.getElementById('m_val').value;
        }

        const btnCalcular = document.getElementById('btn-calcular');
        const iconoOriginal = btnCalcular.innerHTML;
        btnCalcular.disabled = true;
        btnCalcular.innerHTML = 'Calculando...';

        try {
            const response = await fetch('/api/calcular_integracion', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.error) {
                Swal.fire({
                    title: 'Error',
                    text: result.error,
                    icon: 'error',
                    background: 'var(--bg-card)',
                    color: 'var(--text-primary)'
                });
            } else {
                document.getElementById('resultado-integracion-container').style.display = 'flex';
                
                // Mostrar puntos si es integral simple
                const tablaContainer = document.getElementById('tabla-container');
                const tbody = document.getElementById('tbody-integracion');
                
                if (result.x && result.y && result.x.length > 0) {
                    tablaContainer.style.display = 'block';
                    let rows = '';
                    for (let i = 0; i < result.x.length; i++) {
                        rows += `<tr>
                            <td>${i}</td>
                            <td>${Number(result.x[i]).toFixed(6)}</td>
                            <td>${Number(result.y[i]).toFixed(6)}</td>
                        </tr>`;
                    }
                    tbody.innerHTML = rows;
                } else {
                    tablaContainer.style.display = 'none';
                }

                // Mostrar resultados
                const integralVal = Number(result.integral);
                const formatInt = Number.isInteger(integralVal) ? integralVal : integralVal.toFixed(6);
                
                document.getElementById('resultado-final').innerHTML = `
                    <strong style="color: var(--color-success); font-size: 1.2em; display:block; text-align:center;">Resultado de la Integral:</strong>
                    <div style="font-size: 2rem; color: var(--text-primary); margin-top: 10px; width: 100%; text-align: center;">
                        I ≈ <span style="color: var(--accent-primary); font-weight: bold;">${formatInt}</span>
                    </div>
                `;
                
                document.getElementById('consola-salida').value = result.pasos;
                
                if (typeof playSound !== 'undefined') playSound('success');
            }
        } catch (error) {
            Swal.fire({
                title: 'Error',
                text: 'Hubo un problema de conexión.',
                icon: 'error',
                background: 'var(--bg-card)',
                color: 'var(--text-primary)'
            });
        } finally {
            btnCalcular.disabled = false;
            btnCalcular.innerHTML = iconoOriginal;
        }
    });
});
