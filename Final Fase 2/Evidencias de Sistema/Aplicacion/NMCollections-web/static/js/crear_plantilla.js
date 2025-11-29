// Lógica JS para crear plantilla (extraída)
let elementoCount = 0;

document.addEventListener('DOMContentLoaded', function() {
    const ids = window.CREAR_PLANTILLA_IDS || {};
    const imageInput = document.getElementById(ids.imagenMarco);
    const previewArea = document.getElementById('imagePreview');

    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(evt) {
                    previewArea.innerHTML = `<img src="${evt.target.result}" alt="Preview" class="preview-image">`;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    const form = document.getElementById('plantillaForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            const nombreInput = document.getElementById(ids.nombre);
            if (nombreInput && !nombreInput.value.trim()) {
                e.preventDefault();
                mostrarNotificacion('Por favor, ingresa un nombre para la plantilla', 'warning');
                return false;
            }
            document.getElementById('elemento_count').value = elementoCount;
        });
    }

    // Agregar un elemento por defecto al cargar
    setTimeout(() => { agregarElemento(); }, 100);
});

function agregarElemento() {
    const container = document.getElementById('elementos-container');
    if (!container) return;
    const index = elementoCount;
    const elementoHtml = `
        <div class="elemento-item" id="elemento_${index}">
            <button type="button" class="btn-remove-element" onclick="eliminarElemento(${index})">
                <i class="fas fa-times"></i>
            </button>
            <div class="elemento-header">
                <h5 class="elemento-titulo">Elemento ${index + 1}</h5>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <div class="form-group mb-3">
                        <label class="form-label">Nombre del Parámetro *</label>
                        <input type="text" name="elemento_${index}_nombre" class="form-control" placeholder="Ej: nombre_pokemon, ataque, descripcion" required>
                        <div class="form-text">Este será el nombre del campo que el usuario podrá editar</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="form-group mb-3">
                        <label class="form-label">Tipo de Elemento *</label>
                        <select name="elemento_${index}_tipo" class="form-select" required>
                            <option value="">Seleccionar tipo...</option>
                            <option value="texto">Texto</option>
                            <option value="imagen">Imagen</option>
                            <option value="numero">Número</option>
                        </select>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-3">
                    <div class="form-group mb-3">
                        <label class="form-label">Posición X</label>
                        <input type="number" name="elemento_${index}_x" class="form-control" value="50" min="0" max="1000">
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group mb-3">
                        <label class="form-label">Posición Y</label>
                        <input type="number" name="elemento_${index}_y" class="form-control" value="50" min="0" max="1000">
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group mb-3">
                        <label class="form-label">Ancho</label>
                        <input type="number" name="elemento_${index}_ancho" class="form-control" value="200" min="10" max="1000">
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group mb-3">
                        <label class="form-label">Alto</label>
                        <input type="number" name="elemento_${index}_alto" class="form-control" value="30" min="10" max="1000">
                    </div>
                </div>
            </div>
        </div>`;
    container.insertAdjacentHTML('beforeend', elementoHtml);
    elementoCount++;
}

function eliminarElemento(index) {
    const elemento = document.getElementById(`elemento_${index}`);
    if (elemento) elemento.remove();
}

// Notificaciones reutilizables
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
