/**
 * Configuración Global y por Módulos
 */

const DEFAULT_SETTINGS = {
    decimals: 8,
    angleMode: 'rad',
    nl_error_mode: 'relativo',
    nl_iter_max: 500,
    pol_imag_tol: '1e-10',
    inter_auto_graph: true,
    inter_warn_extrap: true,
    sis_strict_diag: true
};

let appSettings = { ...DEFAULT_SETTINGS };

function loadSettings() {
    const saved = localStorage.getItem('sn_settings');
    if (saved) {
        try {
            appSettings = { ...DEFAULT_SETTINGS, ...JSON.parse(saved) };
        } catch (e) {
            console.error("Error loading settings", e);
        }
    }
}

function saveSettings() {
    localStorage.setItem('sn_settings', JSON.stringify(appSettings));
}

// ─── Funciones Globales ───

window.formatNumber = function(val) {
    if (val === null || val === undefined || isNaN(val)) return val;
    return Number(val).toFixed(appSettings.decimals);
};

window.getAngleMode = function() {
    return appSettings.angleMode;
};

// Obtiene todas las configuraciones para enviarlas en el payload
window.getAdvancedSettings = function() {
    return appSettings;
};

// ─── Lógica para la UI de Configuracion (configuracion.html) ───

function initConfigUI() {
    // Si no estamos en la página de configuración, no hacemos nada más
    if (!document.getElementById('setting-decimals')) return;

    // Cargar valores en los inputs
    document.getElementById('setting-decimals').value = appSettings.decimals;
    document.getElementById('setting-decimals-val').textContent = appSettings.decimals;
    
    document.getElementById('cfg-nl-error-mode').value = appSettings.nl_error_mode;
    document.getElementById('cfg-nl-iter-max').value = appSettings.nl_iter_max;
    
    document.getElementById('cfg-pol-imag-tol').value = appSettings.pol_imag_tol;
    
    document.getElementById('cfg-inter-auto-graph').checked = appSettings.inter_auto_graph;
    document.getElementById('cfg-inter-warn-extrap').checked = appSettings.inter_warn_extrap;
    
    document.getElementById('cfg-sis-strict-diag').checked = appSettings.sis_strict_diag;

    updateAngleButtons(appSettings.angleMode);

    // Eventos visuales
    document.getElementById('setting-decimals').addEventListener('input', function(e) {
        document.getElementById('setting-decimals-val').textContent = e.target.value;
    });
}

window.setAngleMode = function(mode) {
    appSettings.angleMode = mode;
    updateAngleButtons(mode);
};

function updateAngleButtons(mode) {
    const rBtn = document.getElementById('btn-ang-rad');
    const dBtn = document.getElementById('btn-ang-deg');
    if (!rBtn || !dBtn) return;
    
    if (mode === 'rad') {
        rBtn.className = 'seg-btn active';
        dBtn.className = 'seg-btn';
    } else {
        dBtn.className = 'seg-btn active';
        rBtn.className = 'seg-btn';
    }
}

window.saveAllSettings = function() {
    appSettings.decimals = parseInt(document.getElementById('setting-decimals').value);
    appSettings.nl_error_mode = document.getElementById('cfg-nl-error-mode').value;
    appSettings.nl_iter_max = parseInt(document.getElementById('cfg-nl-iter-max').value);
    appSettings.pol_imag_tol = document.getElementById('cfg-pol-imag-tol').value;
    appSettings.inter_auto_graph = document.getElementById('cfg-inter-auto-graph').checked;
    appSettings.inter_warn_extrap = document.getElementById('cfg-inter-warn-extrap').checked;
    appSettings.sis_strict_diag = document.getElementById('cfg-sis-strict-diag').checked;

    saveSettings();
    
    Swal.fire({
        title: '¡Guardado!',
        text: 'Tus configuraciones han sido actualizadas.',
        icon: 'success',
        background: '#1e293b',
        color: '#f8fafc',
        confirmButtonColor: '#6366f1',
        timer: 2000,
        showConfirmButton: false
    });
    
    if (typeof playSound === 'function') playSound('success');
};

// Initialize
loadSettings();
document.addEventListener('DOMContentLoaded', initConfigUI);
