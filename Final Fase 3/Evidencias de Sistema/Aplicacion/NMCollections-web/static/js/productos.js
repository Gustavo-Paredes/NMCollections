function getCSRFToken() {
    const el = document.querySelector('[name=csrfmiddlewaretoken]');
    if (el) return el.value;
    const match = document.cookie.match(/(^|;)\s*csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[2]) : '';
}

let confirmEliminarProductoModal = null;

function mostrarModalEliminarProducto(id) {
    try {
        const modalEl = document.getElementById('confirmEliminarProductoModal');
        const confirmBtn = document.getElementById('confirmEliminarProductoBtn');
        if (!modalEl || !confirmBtn) {
            // Fallback a confirm si el modal no está disponible
            if (confirm('¿Estás seguro de que deseas eliminar este producto?')) {
                eliminarProducto(id);
            }
            return;
        }
        confirmBtn.dataset.productoId = id;
        if (!confirmEliminarProductoModal && window.bootstrap && bootstrap.Modal) {
            confirmEliminarProductoModal = new bootstrap.Modal(modalEl);
        }
        if (confirmEliminarProductoModal) {
            confirmEliminarProductoModal.show();
        } else {
            // Fallback básico si no está bootstrap.Modal
            modalEl.classList.add('show');
            modalEl.style.display = 'block';
            modalEl.removeAttribute('aria-hidden');
        }
    } catch (e) {
        // Último recurso
        if (confirm('¿Estás seguro de que deseas eliminar este producto?')) {
            eliminarProducto(id);
        }
    }
}

// Vincular botón de confirmación del modal
document.addEventListener('DOMContentLoaded', () => {
    const confirmBtn = document.getElementById('confirmEliminarProductoBtn');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', async () => {
            const id = confirmBtn.dataset.productoId;
            if (!id) return;
            await eliminarProducto(id);
            // Cerrar modal
            const modalEl = document.getElementById('confirmEliminarProductoModal');
            if (confirmEliminarProductoModal) {
                confirmEliminarProductoModal.hide();
            } else if (modalEl) {
                modalEl.classList.remove('show');
                modalEl.style.display = 'none';
                modalEl.setAttribute('aria-hidden', 'true');
            }
        });
    }
});

function eliminarProducto(id) {
    fetch(`/productos/eliminar/${id}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'X-Requested-With': 'XMLHttpRequest',
        },
    }).then(async (response) => {
        if (!response.ok) throw new Error('Error HTTP');
        // Si el backend devuelve JSON cuando es AJAX
        let data = null;
        try { data = await response.json(); } catch (e) {}
        // Eliminar la fila del DOM sin recargar
        const row = document.querySelector(`tr[data-producto-id="${id}"]`);
        if (row) row.remove();
        // Si ya no quedan filas, mostrar estado vacío
        const tbody = document.querySelector('table tbody');
        if (tbody && tbody.children.length === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = '<td colspan="7" class="text-center">No se encontraron productos</td>';
            tbody.appendChild(tr);
        }
    }).catch(() => {
        mostrarNotificacion('Error al eliminar el producto', 'error');
    });
}

// Notificación ligera (similar a canvas-editor)
function mostrarNotificacion(mensaje, tipo = 'info') {
    const tipos = {
        success: { icon: 'check-circle', clase: 'success' },
        error: { icon: 'times-circle', clase: 'danger' },
        warning: { icon: 'exclamation-triangle', clase: 'warning' },
        info: { icon: 'info-circle', clase: 'info' }
    };
    const t = tipos[tipo] || tipos.info;
    let contenedor = document.getElementById('nm-toast-container');
    if (!contenedor) {
        contenedor = document.createElement('div');
        contenedor.id = 'nm-toast-container';
        contenedor.style.cssText = 'position:fixed; top:20px; right:20px; z-index:11000; display:flex; flex-direction:column; gap:10px;';
        document.body.appendChild(contenedor);
    }
    const toast = document.createElement('div');
    toast.className = `alert alert-${t.clase} shadow-sm mb-0 py-2 px-3`; 
    toast.style.cssText = 'min-width:260px;';
    toast.innerHTML = `<div class=\"d-flex align-items-start\"><i class=\"fas fa-${t.icon} me-2 mt-1\"></i><div class=\"flex-grow-1\">${mensaje}</div><button type=\"button\" class=\"btn-close ms-2\" style=\"font-size:10px\" aria-label=\"Cerrar\"></button></div>`;
    toast.querySelector('.btn-close').onclick = () => toast.remove();
    contenedor.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}