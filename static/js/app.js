/**
 * JavaScript principal - Aplicación de Ocupabilidad
 * Maneja interacciones del frontend y llamadas AJAX
 */

// ============================================================================
// FUNCIONES GENERALES
// ============================================================================

/**
 * Muestra un mensaje de notificación
 * @param {string} mensaje - Mensaje a mostrar
 * @param {string} tipo - Tipo de notificación (success, error, warning, info)
 */
function mostrarNotificacion(mensaje, tipo = 'info') {
    const alerta = document.createElement('div');
    alerta.className = `alert alert-${tipo} alert-dismissible fade show position-fixed`;
    alerta.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alerta.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alerta);
    
    setTimeout(() => {
        alerta.remove();
    }, 5000);
}

/**
 * Realiza una petición AJAX
 * @param {string} url - URL de la petición
 * @param {object} options - Opciones de la petición
 * @returns {Promise} Promesa con la respuesta
 */
async function peticionAjax(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error en petición AJAX:', error);
        throw error;
    }
}

// ============================================================================
// FUNCIONES PARA EL DASHBOARD
// ============================================================================

/**
 * Carga las estadísticas del dashboard
 */
async function cargarEstadisticas() {
    try {
        const data = await peticionAjax('/api/estadisticas');
        
        if (data.success) {
            document.getElementById('registros-hoy').textContent = data.total_hoy;
            document.getElementById('registros-mes').textContent = data.total_mes;
            document.getElementById('horas-mes').textContent = data.horas_mes + ' h';
        }
    } catch (error) {
        console.error('Error al cargar estadísticas:', error);
    }
}

// ============================================================================
// FUNCIONES PARA EL FORMULARIO DE REGISTRO
// ============================================================================

/**
 * Valida el formulario de registro
 * @returns {boolean} True si es válido
 */
function validarFormulario() {
    const fecha = document.getElementById('fecha');
    const commit = document.getElementById('commit');
    
    if (!fecha.value) {
        mostrarNotificacion('Seleccione una fecha', 'warning');
        return false;
    }
    
    if (!commit.checked) {
        if (!confirm('¿Está seguro de que desea realizar una simulación sin guardar?')) {
            return false;
        }
    }
    
    return true;
}

/**
 * Establece la fecha de hoy en el formulario
 */
function establecerFechaHoy() {
    const fechaInput = document.getElementById('fecha');
    if (fechaInput && !fechaInput.value) {
        const today = new Date().toISOString().split('T')[0];
        fechaInput.value = today;
    }
}

// ============================================================================
// FUNCIONES PARA LA TABLA DE REGISTROS
// ============================================================================

/**
 * Filtra la tabla de registros según el texto de búsqueda
 * @param {string} texto - Texto a buscar
 */
function filtrarTabla(texto) {
    const filas = document.querySelectorAll('#tabla-registros tbody tr');
    const textoLower = texto.toLowerCase();
    
    filas.forEach(fila => {
        const contenido = fila.textContent.toLowerCase();
        fila.style.display = contenido.includes(textoLower) ? '' : 'none';
    });
}

/**
 * Exporta la tabla a CSV
 * @param {string} idTabla - ID de la tabla a exportar
 */
function exportarCSV(idTabla) {
    const tabla = document.getElementById(idTabla);
    if (!tabla) {
        mostrarNotificacion('No se encontró la tabla', 'error');
        return;
    }
    
    let csv = [];
    
    // Obtener encabezados
    const encabezados = [];
    tabla.querySelectorAll('thead th').forEach(th => {
        encabezados.push(th.textContent);
    });
    csv.push(encabezados.join(','));
    
    // Obtener filas visibles
    tabla.querySelectorAll('tbody tr').forEach(tr => {
        if (tr.style.display !== 'none') {
            const fila = [];
            tr.querySelectorAll('td').forEach(td => {
                // Escapar comas y comillas
                let valor = td.textContent;
                if (valor.includes(',') || valor.includes('"')) {
                    valor = '"' + valor.replace(/"/g, '""') + '"';
                }
                fila.push(valor);
            });
            csv.push(fila.join(','));
        }
    });
    
    // Crear y descargar archivo
    const blob = new Blob([csv.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `registros_ocupabilidad_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    mostrarNotificacion('Archivo CSV exportado correctamente', 'success');
}

// ============================================================================
// FUNCIONES PARA VERIFICACIÓN DE BD
// ============================================================================

/**
 * Verifica la conexión a la base de datos
 */
async function verificarConexion() {
    try {
        mostrarNotificacion('Verificando conexión...', 'info');
        
        const data = await peticionAjax('/api/verificar-conexion', {
            method: 'POST'
        });
        
        if (data.success) {
            mostrarNotificacion('✅ ' + data.message, 'success');
        } else {
            mostrarNotificacion('❌ ' + data.message, 'danger');
        }
    } catch (error) {
        mostrarNotificacion('❌ Error al verificar conexión', 'danger');
    }
}

// ============================================================================
// FUNCIONES PARA REPORTES
// ============================================================================

/**
 * Filtra el reporte por fechas
 */
function filtrarReporte() {
    const fechaInicio = document.getElementById('fecha-inicio').value;
    const fechaFin = document.getElementById('fecha-fin').value;
    
    if (!fechaInicio || !fechaFin) {
        mostrarNotificacion('Seleccione ambas fechas para filtrar', 'warning');
        return;
    }
    
    // Filtrar filas de la tabla
    const filas = document.querySelectorAll('#tabla-reporte tbody tr');
    
    filas.forEach(fila => {
        const fechaCelda = fila.cells[5].textContent; // Columna de fecha
        const fecha = new Date(fechaCelda);
        const inicio = new Date(fechaInicio);
        const fin = new Date(fechaFin);
        
        if (fecha >= inicio && fecha <= fin) {
            fila.style.display = '';
        } else {
            fila.style.display = 'none';
        }
    });
    
    mostrarNotificacion('Reporte filtrado correctamente', 'success');
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Establecer fecha de hoy si estamos en el formulario de registro
    establecerFechaHoy();
    
    // Configurar búsqueda en tabla de registros
    const inputBusqueda = document.getElementById('buscar');
    if (inputBusqueda) {
        inputBusqueda.addEventListener('input', function() {
            filtrarTabla(this.value);
        });
    }
    
    // Configurar validación del formulario
    const formulario = document.querySelector('form');
    if (formulario) {
        formulario.addEventListener('submit', function(e) {
            if (!validarFormulario()) {
                e.preventDefault();
            }
        });
    }
    
    // Cargar estadísticas si estamos en el dashboard
    if (document.getElementById('registros-hoy')) {
        cargarEstadisticas();
    }
    
    console.log('Aplicación de Ocupabilidad inicializada');
});

// ============================================================================
// EXPORTAR FUNCIONES (para uso global)
// ============================================================================

window.mostrarNotificacion = mostrarNotificacion;
window.verificarConexion = verificarConexion;
window.filtrarReporte = filtrarReporte;
window.exportarTabla = function() { exportarCSV('tabla-registros'); };
