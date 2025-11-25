/**
 * Canvas Editor - Editor de Trading Cards
 * Gestiona la creación y edición de cartas personalizadas
 */

// ============================================================================
// VARIABLES GLOBALES
// ============================================================================
let canvas;
let canvasReverso;
let plantillaSeleccionada = null;
let elementosActuales = [];
let fondoActual = null;
let marcoEscalado = 'llenar';
let imagenTemporal = null;
let caraActual = 'frente'; // 'frente' o 'reverso'
let imagenPersonalizadaActual = null; // Imagen cargada por el usuario
let imagenEnCanvas = null; // Referencia a la imagen en el canvas

// ============================================================================
// INICIALIZACIÓN
// ============================================================================

/**
 * Verifica que las librerías necesarias estén cargadas
 */
function verificarLibrerias() {
    console.log('🔍 Verificando librerías...');
    const fabricOk = typeof fabric !== 'undefined';
    const axiosOk = typeof axios !== 'undefined';
    
    console.log('   - Fabric.js:', fabricOk ? '✅' : '❌');
    console.log('   - Axios:', axiosOk ? '✅' : '❌');
    
    if (!axiosOk) {
        console.error('❌ Axios no está cargado');
        alert('Error: Axios no se cargó. Recarga la página.');
        return false;
    }
    
    return fabricOk && axiosOk;
}

/**
 * Inicializa el canvas de Fabric.js
 */
function inicializarCanvas() {
    const canvasElement = document.getElementById('cardCanvas');
    const canvasReversoElement = document.getElementById('cardCanvasReverso');
    
    if (!canvasElement) {
        console.error('❌ No se encontró el elemento canvas con id "cardCanvas"');
        return;
    }
    
    console.log('🎨 Elemento canvas encontrado:', canvasElement);
    
    // Canvas frontal
    canvas = new fabric.Canvas('cardCanvas', {
        backgroundColor: '#ffffff',
        width: 320,
        height: 420,
        selection: true,
        renderOnAddRemove: true,
        enableRetinaScaling: true
    });
    

    
    // Event listeners para texto personalizado
    canvas.on('selection:created', function(e) {
        const objeto = e.selected[0];
        console.log('Objeto seleccionado:', objeto);
        if (objeto && objeto.customType === 'texto-personalizado') {
            mostrarControlesTextoSeleccionado();
        }
    });
    
    canvas.on('selection:updated', function(e) {
        const objeto = e.selected[0];
        if (objeto && objeto.customType === 'texto-personalizado') {
            mostrarControlesTextoSeleccionado();
        } else {
            ocultarControlesTextoSeleccionado();
        }
    });
    
    canvas.on('selection:cleared', function() {
        ocultarControlesTextoSeleccionado();
    });
    
    // Listeners para actualización en tiempo real del texto seleccionado
    setTimeout(() => {
        const fuenteSelect = document.getElementById('fuenteSelect');
        const tamañoTexto = document.getElementById('tamañoTexto');
        const colorTexto = document.getElementById('colorTexto');
        const textoNegrita = document.getElementById('textoNegrita');
        const textoCursiva = document.getElementById('textoCursiva');
        const textoSubrayado = document.getElementById('textoSubrayado');
        
        if (fuenteSelect) fuenteSelect.addEventListener('change', actualizarTextoSeleccionado);
        if (tamañoTexto) tamañoTexto.addEventListener('input', actualizarTextoSeleccionado);
        if (colorTexto) colorTexto.addEventListener('change', actualizarTextoSeleccionado);
        if (textoNegrita) textoNegrita.addEventListener('change', actualizarTextoSeleccionado);
        if (textoCursiva) textoCursiva.addEventListener('change', actualizarTextoSeleccionado);
        if (textoSubrayado) textoSubrayado.addEventListener('change', actualizarTextoSeleccionado);
        
        document.querySelectorAll('input[name="alineacionTexto"]').forEach(radio => {
            radio.addEventListener('change', actualizarTextoSeleccionado);
        });
    }, 500);
}

/**
 * Configura CSRF token para peticiones Django
 */
function configurarCSRF() {
    const csrftoken = getCookie('csrftoken');
    axios.defaults.headers.common['X-CSRFToken'] = csrftoken;
}

/**
 * Obtiene el valor de una cookie
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Inicialización al cargar el DOM
 */
document.addEventListener('DOMContentLoaded', function() {
    if (!verificarLibrerias()) return;
    
    configurarCSRF();
    inicializarCanvas();
    cargarPlantillas();
    
    // Verificar si hay una carta a cargar
    const urlParams = new URLSearchParams(window.location.search);
    const cartaId = urlParams.get('carta_id');
    
    if (cartaId) {
        console.log('📂 Cargando carta ID:', cartaId);
        cargarCartaExistente(cartaId);
    } else {
        console.log('✨ Modo creación de nueva carta');
    }
});

// ============================================================================
// GESTIÓN DE UI
// ============================================================================

/**
 * Muestra u oculta el overlay de carga
 */
function mostrarLoading(show = true, mensaje = 'Cargando...') {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = show ? 'flex' : 'none';
    
    if (show && mensaje) {
        let loadingText = overlay.querySelector('.loading-text');
        if (!loadingText) {
            loadingText = document.createElement('p');
            loadingText.className = 'loading-text';
            loadingText.style.cssText = 'color: white; margin-top: 20px; font-size: 18px;';
            overlay.appendChild(loadingText);
        }
        loadingText.textContent = mensaje;
    }
}

/**
 * Muestra una notificación temporal
 */
function mostrarNotificacion(mensaje, tipo = 'info') {
    const notificacion = document.createElement('div');
    const iconClass = tipo === 'success' ? 'check-circle' : 'exclamation-triangle';
    const alertClass = tipo === 'success' ? 'success' : 'danger';
    
    notificacion.className = `alert alert-${alertClass} position-fixed`;
    notificacion.style.cssText = 'top: 20px; right: 20px; z-index: 10000; min-width: 300px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);';
    notificacion.innerHTML = `
        <i class="fas fa-${iconClass}"></i> ${mensaje}
        <button type="button" class="btn-close float-end" onclick="this.parentElement.remove()"></button>
    `;
    
    document.body.appendChild(notificacion);
    setTimeout(() => notificacion.remove(), 5000);
}

// ============================================================================
// GESTIÓN DE PLANTILLAS
// ============================================================================

/**
 * Carga las plantillas disponibles desde la API
 */
async function cargarPlantillas() {
    try {
        console.log('🔄 Cargando plantillas...');
        mostrarLoading(true);
        
        const response = await axios.get('/personalizacion/canvas-editor/plantillas_disponibles/');
        const plantillas = response.data;
        
        console.log('✅ Plantillas recibidas:', plantillas.length);
        
        const container = document.getElementById('plantillasContainer');
        if (!container) {
            throw new Error('Contenedor de plantillas no encontrado');
        }
        
        container.innerHTML = '';
        
        if (!plantillas || plantillas.length === 0) {
            container.innerHTML = '<p class="text-warning text-center p-3"><i class="fas fa-exclamation-triangle"></i><br>No hay plantillas disponibles</p>';
            return;
        }
        
        plantillas.forEach(plantilla => {
            container.appendChild(crearTarjetaPlantilla(plantilla));
        });
        
        console.log('✅ Plantillas renderizadas');
        
    } catch (error) {
        console.error('❌ Error cargando plantillas:', error);
        mostrarErrorPlantillas(error);
    } finally {
        mostrarLoading(false);
    }
}

/**
 * Crea el elemento HTML para una tarjeta de plantilla
 */
function crearTarjetaPlantilla(plantilla) {
    const div = document.createElement('div');
    div.className = 'plantilla-card';
    div.dataset.plantillaId = plantilla.id; // Agregar ID para búsqueda posterior
    
    let html = `
        <h6><i class="fas fa-id-card"></i> ${plantilla.nombre}</h6>
        <p style="font-size: 12px; margin-bottom: 8px;">${plantilla.descripcion || ''}</p>
        <small class="badge bg-info">${plantilla.tipo_carta}</small>
    `;
    
    if (plantilla.diseñador) {
        html += `
            <div style="margin-top: 8px;">
                <small class="badge bg-secondary">
                    <i class="fas fa-palette"></i> ${plantilla.diseñador}
                </small>
            </div>
        `;
    }
    
    if (plantilla.imagen_marco_url) {
        html += `
            <div style="margin-top: 5px;">
                <small class="text-warning">
                    <i class="fas fa-star"></i> Marco Profesional
                </small>
            </div>
        `;
    }
    
    div.innerHTML = html;
    div.onclick = () => seleccionarPlantilla(plantilla);
    
    return div;
}

/**
 * Muestra un mensaje de error al cargar plantillas
 */
function mostrarErrorPlantillas(error) {
    const container = document.getElementById('plantillasContainer');
    const es403 = error.response?.status === 403;
    
    container.innerHTML = `
        <div class="alert alert-${es403 ? 'warning' : 'danger'}">
            <i class="fas fa-${es403 ? 'lock' : 'exclamation-triangle'}"></i> 
            <strong>${es403 ? 'Acceso denegado' : 'Error cargando plantillas'}</strong><br>
            <small>${es403 ? 'Necesitas estar logueado' : error.message}</small>
        </div>
    `;
}

/**
 * Selecciona una plantilla y la carga en el canvas
 */
function seleccionarPlantilla(plantilla) {
    console.log('🎨 Seleccionando plantilla:', plantilla.nombre);
    
    // Actualizar UI
    document.querySelectorAll('.plantilla-card').forEach(card => card.classList.remove('active'));
    event.target.closest('.plantilla-card').classList.add('active');
    
    // Guardar referencia
    plantillaSeleccionada = plantilla;
    elementosActuales = plantilla.elementos || [];
    fondoActual = plantilla.fondo;
    
    // Habilitar tabs
    ['tab-imagenes', 'tab-texto', 'tab-formas', 'tab-capas'].forEach(id => {
        document.getElementById(id).disabled = false;
    });
    
    // Limpiar y cargar marco
    canvas.clear();
    cargarMarcoPlantilla(plantilla);
    generarControlesElementos();
}

/**
 * Carga el marco/fondo de la plantilla en el canvas
 */
function cargarMarcoPlantilla(plantilla) {
    if (!plantilla.imagen_marco_url) {
        aplicarFondoSimple(fondoActual);
        document.getElementById('marcoControls').style.display = 'none';
        return;
    }
    
    console.log('🖼️ Cargando marco:', plantilla.imagen_marco_url);
    
    // Verificar accesibilidad de la imagen
    const testImg = new Image();
    
    testImg.onload = function() {
        console.log('✅ Imagen accesible:', testImg.width + 'x' + testImg.height);
        cargarMarcoConFabric(plantilla.imagen_marco_url);
    };
    
    testImg.onerror = function() {
        console.error('❌ No se puede acceder a la imagen');
        alert('No se pudo cargar la imagen del marco.\nVerifica que el servidor Django esté corriendo.');
        canvas.setBackgroundColor('#ffffff', canvas.renderAll.bind(canvas));
    };
    
    testImg.src = plantilla.imagen_marco_url;
}

/**
 * Carga la imagen del marco usando Fabric.js con mejor ajuste
 */
function cargarMarcoConFabric(url) {
    console.log('🔄 Iniciando carga con Fabric.js...');
    console.log('   URL:', url);
    
    const canvasActivo = caraActual === 'frente' ? canvas : canvasReverso;
    
    fabric.Image.fromURL(url, function(img) {
        if (!img) {
            console.error('❌ Fabric devolvió null');
            canvasActivo.setBackgroundColor('#ffffff', canvasActivo.renderAll.bind(canvasActivo));
            return;
        }
        
        console.log('✅ Imagen cargada en Fabric');
        console.log('   - Dimensiones originales:', img.width, 'x', img.height);
        
        // Calcular escala para ajustar al canvas
        const canvasWidth = canvasActivo.width;
        const canvasHeight = canvasActivo.height;
        const imgRatio = img.width / img.height;
        const canvasRatio = canvasWidth / canvasHeight;
        
        let scale;
        if (marcoEscalado === 'llenar') {
            // Cubrir todo el canvas (puede recortar)
            scale = imgRatio > canvasRatio 
                ? canvasHeight / img.height 
                : canvasWidth / img.width;
        } else {
            // Ajustar manteniendo proporción (puede dejar espacios)
            scale = imgRatio > canvasRatio 
                ? canvasWidth / img.width 
                : canvasHeight / img.height;
        }
        
        console.log('📏 Ajuste de imagen:');
        console.log('   - Ratio imagen:', imgRatio.toFixed(2));
        console.log('   - Ratio canvas:', canvasRatio.toFixed(2));
        console.log('   - Scale final:', scale.toFixed(4));
        console.log('   - Modo:', marcoEscalado);
        
        // Aplicar escala y centrar
        img.scale(scale);
        
        const scaledWidth = img.getScaledWidth();
        const scaledHeight = img.getScaledHeight();
        
        console.log('📐 Dimensiones escaladas:', scaledWidth.toFixed(2), 'x', scaledHeight.toFixed(2));
        
        img.set({
            left: (canvasWidth - scaledWidth) / 2,
            top: (canvasHeight - scaledHeight) / 2,
            selectable: false,
            evented: false,
            hasControls: false,
            hasBorders: false,
            lockMovementX: true,
            lockMovementY: true,
            customId: 'marco_plantilla'
        });
        
        console.log('📍 Posición final:', 'left=' + img.left.toFixed(2), 'top=' + img.top.toFixed(2));
        
        // Limpiar canvas antes de agregar
        canvasActivo.clear();
        canvasActivo.backgroundColor = '#ffffff';
        
        // Agregar la imagen
        canvasActivo.add(img);
        img.sendToBack();
        
        console.log('📊 Estado del canvas después de agregar:');
        console.log('   - Total objetos:', canvasActivo.getObjects().length);
        
        // Renderizar
        canvasActivo.renderAll();
        console.log('🎨 Renderización completada');
        
        // Mostrar controles
        document.getElementById('marcoControls').style.display = 'block';
        document.getElementById('tipoEscalado').value = marcoEscalado;
        
        console.log('✅ Proceso de carga completado');
        
    }, { 
        crossOrigin: 'anonymous'
    });
}

/**
 * Aplica un fondo simple (color o gradiente)
 */
function aplicarFondoSimple(fondo) {
    if (!fondo) {
        canvas.setBackgroundColor('#ffffff', canvas.renderAll.bind(canvas));
        return;
    }
    
    if (fondo.tipo_fondo === 'color' || fondo.tipo_fondo === 'gradiente') {
        canvas.setBackgroundColor(fondo.valor, canvas.renderAll.bind(canvas));
    }
}

/**
 * Cambia el tipo de escalado del marco
 */
function cambiarEscaladoMarco(tipo) {
    marcoEscalado = tipo;
    if (plantillaSeleccionada?.imagen_marco_url) {
        cargarMarcoConFabric(plantillaSeleccionada.imagen_marco_url);
    }
}

/**
 * Cambia entre la vista de frente y reverso de la carta
 */
function cambiarCara(cara) {
    caraActual = cara;
    
    // Actualizar botones activos
    document.querySelectorAll('.cara-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`btn-${cara}`).classList.add('active');
    
    // Mostrar/ocultar canvas
    const contenedorFrente = document.getElementById('canvas-frente');
    const contenedorReverso = document.getElementById('canvas-reverso');
    
    if (cara === 'frente') {
        contenedorFrente.style.display = 'flex';
        contenedorReverso.style.display = 'none';
    } else {
        contenedorFrente.style.display = 'none';
        contenedorReverso.style.display = 'flex';
    }
    
    console.log('🔄 Cambiado a cara:', cara);
}

// ============================================================================
// GESTIÓN DE IMÁGENES PERSONALIZADAS
// ============================================================================

/**
 * Maneja la subida de una imagen personalizada
 */
function subirImagenPersonalizada(archivo) {
    if (!archivo) return;
    
    if (!archivo.type.startsWith('image/')) {
        alert('Por favor selecciona un archivo de imagen válido');
        return;
    }
    
    console.log('📤 Subiendo imagen:', archivo.name);
    mostrarLoading(true, 'Cargando imagen...');
    
    const reader = new FileReader();
    reader.onload = function(e) {
        imagenPersonalizadaActual = {
            data: e.target.result,
            archivo: archivo,
            nombre: archivo.name
        };
        
        // Mostrar preview
        const preview = document.getElementById('previewImagenPersonalizada');
        const imgPreview = document.getElementById('imgPreview');
        imgPreview.src = e.target.result;
        preview.style.display = 'block';
        
        console.log('✅ Imagen cargada:', archivo.name);
        mostrarLoading(false);
    };
    
    reader.onerror = function() {
        console.error('❌ Error leyendo archivo');
        alert('Error al cargar la imagen');
        mostrarLoading(false);
    };
    
    reader.readAsDataURL(archivo);
}

/**
 * Aplica la imagen al canvas sin recorte
 */
function aplicarImagenAlCanvas() {
    if (!imagenPersonalizadaActual) {
        alert('Primero sube una imagen');
        return;
    }
    
    const canvasActivo = caraActual === 'frente' ? canvas : canvasReverso;
    
    fabric.Image.fromURL(imagenPersonalizadaActual.data, function(img) {
        // Escalar para que quepa en el canvas
        const scale = Math.min(
            canvasActivo.width / img.width,
            canvasActivo.height / img.height
        ) * 0.8; // 80% del tamaño para dejar margen
        
        img.set({
            left: canvasActivo.width / 2,
            top: canvasActivo.height / 2,
            originX: 'center',
            originY: 'center',
            scaleX: scale,
            scaleY: scale,
            customId: 'imagen_personalizada',
            selectable: true,
            hasControls: true,
            hasBorders: true
        });
        
        // Eliminar imagen anterior si existe
        if (imagenEnCanvas) {
            canvasActivo.remove(imagenEnCanvas);
        }
        
        canvasActivo.add(img);
        imagenEnCanvas = img;
        canvasActivo.setActiveObject(img);
        canvasActivo.renderAll();
        
        // Mostrar opciones de ajuste
        document.getElementById('opcionesImagen').style.display = 'block';
        
        console.log('✅ Imagen aplicada al canvas');
    });
}

/**
 * Aplica recorte automático de persona a la imagen
 */
async function aplicarRecorteInteligente() {
    if (!imagenPersonalizadaActual) {
        alert('Primero sube una imagen');
        return;
    }
    
    try {
        mostrarLoading(true, 'Recortando persona automáticamente...');
        
        const formData = new FormData();
        formData.append('imagen', imagenPersonalizadaActual.archivo);
        formData.append('tipo_elemento', 'foto_jugador');
        formData.append('ancho', 300);
        formData.append('alto', 400);
        
        console.log('🔄 Enviando imagen para recorte inteligente...');
        
        const response = await axios.post(
            '/personalizacion/canvas-editor/recorte_inteligente/',
            formData,
            { 
                headers: { 'Content-Type': 'multipart/form-data' },
                timeout: 30000 // 30 segundos de timeout
            }
        );
        
        if (response.data.url_imagen_procesada) {
            console.log('✅ Imagen recortada:', response.data.url_imagen_procesada);
            
            // Actualizar la imagen actual con la procesada
            imagenPersonalizadaActual.data = response.data.url_imagen_procesada;
            imagenPersonalizadaActual.procesada = true;
            
            // Actualizar preview
            document.getElementById('imgPreview').src = response.data.url_imagen_procesada;
            
            // Aplicar al canvas
            const canvasActivo = caraActual === 'frente' ? canvas : canvasReverso;
            
            fabric.Image.fromURL(response.data.url_imagen_procesada, function(img) {
                const scale = Math.min(
                    canvasActivo.width / img.width,
                    canvasActivo.height / img.height
                ) * 0.9;
                
                img.set({
                    left: canvasActivo.width / 2,
                    top: canvasActivo.height / 2,
                    originX: 'center',
                    originY: 'center',
                    scaleX: scale,
                    scaleY: scale,
                    customId: 'imagen_personalizada_recortada',
                    selectable: true,
                    hasControls: true,
                    hasBorders: true
                });
                
                // Eliminar imagen anterior si existe
                if (imagenEnCanvas) {
                    canvasActivo.remove(imagenEnCanvas);
                }
                
                canvasActivo.add(img);
                imagenEnCanvas = img;
                canvasActivo.setActiveObject(img);
                canvasActivo.renderAll();
                
                // Mostrar opciones de ajuste
                document.getElementById('opcionesImagen').style.display = 'block';
                
                console.log('✅ Imagen recortada aplicada al canvas');
            }, { crossOrigin: 'anonymous' });
            
            mostrarNotificacion('¡Persona recortada automáticamente!', 'success');
        }
        
    } catch (error) {
        console.error('❌ Error en recorte inteligente:', error);
        
        let mensaje = 'Error procesando la imagen';
        if (error.response?.data?.error) {
            mensaje = error.response.data.error;
        } else if (error.code === 'ECONNABORTED') {
            mensaje = 'La operación tardó demasiado. Intenta con una imagen más pequeña.';
        }
        
        mostrarNotificacion(mensaje, 'error');
    } finally {
        mostrarLoading(false);
    }
}

/**
 * Ajusta la imagen en el canvas según el modo
 */
function ajustarImagenEnCanvas(modo) {
    if (!imagenEnCanvas) {
        alert('Primero aplica una imagen al canvas');
        return;
    }
    
    const canvasActivo = caraActual === 'frente' ? canvas : canvasReverso;
    const img = imagenEnCanvas;
    
    switch(modo) {
        case 'center':
            // Centrar sin cambiar escala
            img.set({
                left: canvasActivo.width / 2,
                top: canvasActivo.height / 2,
                originX: 'center',
                originY: 'center'
            });
            break;
            
        case 'fill':
            // Llenar todo el canvas (puede recortar)
            const fillScale = Math.max(
                canvasActivo.width / (img.width * img.scaleX),
                canvasActivo.height / (img.height * img.scaleY)
            );
            img.set({
                scaleX: img.scaleX * fillScale,
                scaleY: img.scaleY * fillScale,
                left: canvasActivo.width / 2,
                top: canvasActivo.height / 2,
                originX: 'center',
                originY: 'center'
            });
            break;
            
        case 'fit':
            // Ajustar manteniendo proporción completa
            const fitScale = Math.min(
                canvasActivo.width / img.width,
                canvasActivo.height / img.height
            ) * 0.9;
            img.set({
                scaleX: fitScale,
                scaleY: fitScale,
                left: canvasActivo.width / 2,
                top: canvasActivo.height / 2,
                originX: 'center',
                originY: 'center'
            });
            break;
    }
    
    canvasActivo.renderAll();
    console.log('✅ Imagen ajustada:', modo);
}

/**
 * Limpia la imagen personalizada
 */
function limpiarImagenPersonalizada() {
    // Limpiar del canvas
    if (imagenEnCanvas) {
        const canvasActivo = caraActual === 'frente' ? canvas : canvasReverso;
        canvasActivo.remove(imagenEnCanvas);
        canvasActivo.renderAll();
        imagenEnCanvas = null;
    }
    
    // Limpiar referencias
    imagenPersonalizadaActual = null;
    
    // Ocultar UI
    document.getElementById('previewImagenPersonalizada').style.display = 'none';
    document.getElementById('opcionesImagen').style.display = 'none';
    document.getElementById('imagenPersonalizada').value = '';
    
    console.log('🗑️ Imagen personalizada eliminada');
}

// ============================================================================
// GESTIÓN DE ELEMENTOS
// ============================================================================

/**
 * Genera los controles de edición para los elementos de la plantilla
 */
function generarControlesElementos() {
    const container = document.getElementById('elementosContainer');
    container.innerHTML = '';
    
    elementosActuales.forEach(elemento => {
        const control = crearControlElemento(elemento);
        if (control) container.appendChild(control);
    });
}

/**
 * Crea el control HTML para un elemento
 */
function crearControlElemento(elemento) {
    const div = document.createElement('div');
    div.className = 'element-input';
    
    const label = elemento.nombre_parametro.replace('_', ' ').toUpperCase();
    const inputId = `param_${elemento.nombre_parametro}`;
    
    switch(elemento.tipo_elemento) {
        case 'texto':
            div.innerHTML = `
                <label>${label}</label>
                <input type="text" id="${inputId}" 
                       placeholder="Ingresa ${label.toLowerCase()}"
                       onchange="actualizarElemento('${elemento.nombre_parametro}', this.value)">
            `;
            break;
            
        case 'color':
            div.innerHTML = `
                <label>${label}</label>
                <input type="color" id="${inputId}" 
                       value="${elemento.color || '#000000'}"
                       onchange="actualizarElemento('${elemento.nombre_parametro}', this.value)">
            `;
            break;
            
        case 'imagen':
            div.innerHTML = `
                <label>${label}</label>
                <div class="image-input-container">
                    <input type="file" id="${inputId}" accept="image/*" style="display: none;"
                           onchange="manejarImagenSubida('${elemento.nombre_parametro}', this.files[0])">
                    <button class="btn btn-outline-light btn-sm w-100" 
                            onclick="document.getElementById('${inputId}').click()">
                        <i class="fas fa-upload"></i> Subir Imagen
                    </button>
                    <button class="btn btn-outline-warning btn-sm w-100 mt-2" 
                            onclick="procesarConRecorteInteligente('${elemento.nombre_parametro}')">
                        <i class="fas fa-magic"></i> Recorte Inteligente
                    </button>
                    <div id="preview_${elemento.nombre_parametro}" class="image-preview mt-2" style="display: none;">
                        <img class="preview-img" style="max-width: 100%; max-height: 100px; border-radius: 5px;">
                        <button class="btn btn-sm btn-danger mt-1" 
                                onclick="removerImagen('${elemento.nombre_parametro}')">
                            <i class="fas fa-trash"></i> Remover
                        </button>
                    </div>
                </div>
            `;
            break;
    }
    
    return div;
}

/**
 * Actualiza un elemento en el canvas
 */
function actualizarElemento(nombreParametro, valor) {
    const elemento = elementosActuales.find(e => e.nombre_parametro === nombreParametro);
    if (!elemento) return;
    
    let objeto = canvas.getObjects().find(obj => obj.customId === nombreParametro);
    
    if (elemento.tipo_elemento === 'texto') {
        if (valor.startsWith('#')) {
            elemento.color = valor;
            if (objeto) objeto.set('fill', valor);
        } else {
            elemento.texto = valor;
            if (objeto) {
                objeto.set('text', valor);
            } else {
                objeto = new fabric.Text(valor, {
                    left: elemento.posicion_x,
                    top: elemento.posicion_y,
                    fontFamily: elemento.fuente || 'Arial',
                    fontSize: elemento.tamaño_fuente || 16,
                    fill: elemento.color || '#000000',
                    customId: nombreParametro
                });
                canvas.add(objeto);
                objeto.bringToFront();
            }
        }
    } else if (elemento.tipo_elemento === 'color') {
        if (nombreParametro.includes('fondo') || nombreParametro.includes('primario')) {
            canvas.setBackgroundColor(valor, canvas.renderAll.bind(canvas));
        }
    }
    
    canvas.renderAll();
}

// ============================================================================
// GESTIÓN DE IMÁGENES
// ============================================================================

/**
 * Maneja la subida de una imagen
 */
function manejarImagenSubida(nombreParametro, archivo) {
    if (!archivo) return;
    
    imagenTemporal = { nombreParametro, archivo };
    mostrarPreviewImagen(nombreParametro, archivo);
    cargarImagen(nombreParametro, archivo);
}

/**
 * Muestra el preview de una imagen
 */
function mostrarPreviewImagen(nombreParametro, archivo) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.getElementById(`preview_${nombreParametro}`);
        preview.querySelector('.preview-img').src = e.target.result;
        preview.style.display = 'block';
    };
    reader.readAsDataURL(archivo);
}

/**
 * Carga una imagen en el canvas (para elementos de plantilla)
 */
function cargarImagen(nombreParametro, archivo) {
    const elemento = elementosActuales.find(el => el.nombre_parametro === nombreParametro);
    if (!elemento) return;
    
    const canvasActivo = caraActual === 'frente' ? canvas : canvasReverso;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        fabric.Image.fromURL(e.target.result, function(img) {
            const objetoAnterior = canvasActivo.getObjects().find(obj => obj.customId === nombreParametro);
            if (objetoAnterior) canvasActivo.remove(objetoAnterior);
            
            img.set({
                left: elemento.posicion_x,
                top: elemento.posicion_y,
                scaleX: elemento.ancho / img.width,
                scaleY: elemento.alto / img.height,
                customId: nombreParametro,
                selectable: true,
                hasControls: true
            });
            
            canvasActivo.add(img);
            img.bringToFront();
            canvasActivo.renderAll();
        });
    };
    reader.readAsDataURL(archivo);
}

/**
 * Carga una imagen desde una URL
 */
function cargarImagenDesdeURL(nombreParametro, url) {
    const elemento = elementosActuales.find(el => el.nombre_parametro === nombreParametro);
    if (!elemento) return;
    
    fabric.Image.fromURL(url, function(img) {
        const objetoAnterior = canvas.getObjects().find(obj => obj.customId === nombreParametro);
        if (objetoAnterior) canvas.remove(objetoAnterior);
        
        img.set({
            left: elemento.posicion_x,
            top: elemento.posicion_y,
            scaleX: elemento.ancho / img.width,
            scaleY: elemento.alto / img.height,
            customId: nombreParametro
        });
        
        canvas.add(img);
        img.bringToFront();
        canvas.renderAll();
    }, { crossOrigin: 'anonymous' });
}

/**
 * Remueve una imagen del canvas
 */
function removerImagen(nombreParametro) {
    const objeto = canvas.getObjects().find(obj => obj.customId === nombreParametro);
    if (objeto) {
        canvas.remove(objeto);
        canvas.renderAll();
    }
    
    document.getElementById(`preview_${nombreParametro}`).style.display = 'none';
    document.getElementById(`param_${nombreParametro}`).value = '';
    
    if (imagenTemporal?.nombreParametro === nombreParametro) {
        imagenTemporal = null;
    }
}

/**
 * Procesa una imagen con recorte inteligente
 */
async function procesarConRecorteInteligente(nombreParametro) {
    if (!imagenTemporal || imagenTemporal.nombreParametro !== nombreParametro) {
        alert('Primero sube una imagen para procesarla');
        return;
    }
    
    try {
        mostrarLoading(true, 'Procesando imagen...');
        
        const elemento = elementosActuales.find(e => e.nombre_parametro === nombreParametro);
        const formData = new FormData();
        formData.append('imagen', imagenTemporal.archivo);
        formData.append('tipo_elemento', nombreParametro);
        formData.append('ancho', elemento?.ancho || 400);
        formData.append('alto', elemento?.alto || 450);
        
        const response = await axios.post(
            '/personalizacion/canvas-editor/recorte_inteligente/',
            formData,
            { headers: { 'Content-Type': 'multipart/form-data' } }
        );
        
        if (response.data.url_imagen_procesada) {
            cargarImagenDesdeURL(nombreParametro, response.data.url_imagen_procesada);
            
            const preview = document.getElementById(`preview_${nombreParametro}`);
            preview.querySelector('.preview-img').src = response.data.url_imagen_procesada;
            
            mostrarNotificacion('¡Recorte inteligente aplicado exitosamente!', 'success');
        }
        
    } catch (error) {
        console.error('❌ Error en recorte inteligente:', error);
        const mensaje = error.response?.data?.error || 'Error procesando la imagen';
        mostrarNotificacion(mensaje, 'error');
    } finally {
        mostrarLoading(false);
    }
}

// ============================================================================
// TEXTO PERSONALIZADO
// ============================================================================

let textoSeleccionado = null;

/**
 * Agrega texto personalizado al canvas
 */
function agregarTextoAlCanvas() {
    const texto = document.getElementById('textoInput').value.trim();
    if (!texto) {
        alert('Por favor, escribe un texto');
        return;
    }
    
    const canvasActivo = caraActual === 'frente' ? canvas : canvasReverso;
    
    // Obtener configuración del texto
    const fuente = document.getElementById('fuenteSelect').value;
    const tamaño = parseInt(document.getElementById('tamañoTexto').value);
    const color = document.getElementById('colorTexto').value;
    const negrita = document.getElementById('textoNegrita').checked;
    const cursiva = document.getElementById('textoCursiva').checked;
    const subrayado = document.getElementById('textoSubrayado').checked;
    const alineacion = document.querySelector('input[name="alineacionTexto"]:checked').value;
    
    // Construir estilo de fuente
    let estiloFuente = '';
    if (cursiva) estiloFuente += 'italic ';
    if (negrita) estiloFuente += 'bold ';
    estiloFuente += tamaño + 'px ';
    estiloFuente += fuente;
    
    // Crear texto en Fabric.js
    const fabricTexto = new fabric.Text(texto, {
        left: canvasActivo.width / 2,
        top: canvasActivo.height / 2,
        fontFamily: fuente,
        fontSize: tamaño,
        fill: color,
        fontWeight: negrita ? 'bold' : 'normal',
        fontStyle: cursiva ? 'italic' : 'normal',
        underline: subrayado,
        textAlign: alineacion,
        originX: 'center',
        originY: 'center',
        selectable: true,
        hasControls: true,
        lockUniScaling: false,
        customType: 'texto-personalizado'
    });
    
    canvasActivo.add(fabricTexto);
    fabricTexto.bringToFront();
    canvasActivo.setActiveObject(fabricTexto);
    canvasActivo.renderAll();
    
    // Limpiar formulario
    document.getElementById('textoInput').value = '';
    
    console.log('✅ Texto agregado al canvas:', texto);
}

/**
 * Elimina el texto seleccionado del canvas
 */
function eliminarTextoSeleccionado() {
    const canvasActivo = caraActual === 'frente' ? canvas : canvasReverso;
    const objetoActivo = canvasActivo.getActiveObject();
    
    if (objetoActivo && objetoActivo.customType === 'texto-personalizado') {
        canvasActivo.remove(objetoActivo);
        canvasActivo.renderAll();
        ocultarControlesTextoSeleccionado();
        console.log('✅ Texto eliminado del canvas');
    }
}

/**
 * Muestra los controles cuando se selecciona un texto
 */
function mostrarControlesTextoSeleccionado() {
    document.getElementById('textoSeleccionadoControles').style.display = 'block';
}

/**
 * Oculta los controles de texto seleccionado
 */
function ocultarControlesTextoSeleccionado() {
    document.getElementById('textoSeleccionadoControles').style.display = 'none';
}

/**
 * Actualiza las propiedades del texto seleccionado
 */
function actualizarTextoSeleccionado() {
    const canvasActivo = caraActual === 'frente' ? canvas : canvasReverso;
    const objetoActivo = canvasActivo.getActiveObject();
    
    if (objetoActivo && (objetoActivo.type === 'text' || objetoActivo.type === 'i-text')) {
        const fuente = document.getElementById('fuenteSelect').value;
        const tamaño = parseInt(document.getElementById('tamañoTexto').value);
        const color = document.getElementById('colorTexto').value;
        const negrita = document.getElementById('textoNegrita').checked;
        const cursiva = document.getElementById('textoCursiva').checked;
        const subrayado = document.getElementById('textoSubrayado').checked;
        const alineacion = document.querySelector('input[name="alineacionTexto"]:checked').value;
        
        objetoActivo.set({
            fontFamily: fuente,
            fontSize: tamaño,
            fill: color,
            fontWeight: negrita ? 'bold' : 'normal',
            fontStyle: cursiva ? 'italic' : 'normal',
            underline: subrayado,
            textAlign: alineacion
        });
        
        canvasActivo.renderAll();
        console.log('✅ Texto actualizado');
    }
}

// ============================================================================
// GUARDAR Y FINALIZAR
// ============================================================================

/**
 * Guarda la carta como borrador
 */
async function guardarCarta() {
    if (!plantillaSeleccionada) {
        alert('Selecciona una plantilla primero');
        return null;
    }
    
    try {
        mostrarLoading(true, 'Guardando carta...');
        
        const parametros = elementosActuales
            .map(elemento => {
                const input = document.getElementById(`param_${elemento.nombre_parametro}`);
                return input?.value ? {
                    nombre_parametro: elemento.nombre_parametro,
                    tipo_parametro: elemento.tipo_elemento,
                    valor: input.value
                } : null;
            })
            .filter(p => p !== null);
        
        const data = {
            plantilla_id: plantillaSeleccionada.id,
            nombre_carta: document.getElementById('nombreCarta').value,
            parametros
        };
        
        const response = await axios.post('/personalizacion/canvas-editor/guardar_carta_temporal/', data);
        
        // Guardar imágenes PNG de ambas caras si tenemos ID
        const cartaId = response.data?.carta_id;
        if (cartaId) {
            await guardarImagenesCartas(cartaId);
        }
        
        alert('¡Carta guardada exitosamente como borrador!');
        console.log('✅ Carta guardada:', response.data);
        
        return cartaId;
        
    } catch (error) {
        console.error('❌ Error guardando carta:', error);
        const errorMsg = error.response?.data?.error || error.message || 'Error desconocido';
        alert(`Error guardando la carta: ${errorMsg}`);
        return null;
    } finally {
        mostrarLoading(false);
    }
}

/**
 * Guarda las imágenes PNG de ambas caras de la carta
 */
async function guardarImagenesCartas(cartaId) {
    try {
        // Guardar frente
        const imagenFrente = canvas.toDataURL('image/png');
        const formDataFrente = new FormData();
        formDataFrente.append('imagen_data', imagenFrente);
        formDataFrente.append('cara', 'frente');
        
        await axios.post(`/personalizacion/guardar-imagen/${cartaId}/`, formDataFrente);
        console.log('✅ Imagen frente guardada');
        
        // Guardar reverso si existe
        if (canvasReverso && canvasReverso.getObjects().length > 0) {
            const imagenReverso = canvasReverso.toDataURL('image/png');
            const formDataReverso = new FormData();
            formDataReverso.append('imagen_data', imagenReverso);
            formDataReverso.append('cara', 'reverso');
            
            await axios.post(`/personalizacion/guardar-imagen/${cartaId}/`, formDataReverso);
            console.log('✅ Imagen reverso guardada');
        }
    } catch (error) {
        console.warn('⚠️ Error guardando imágenes:', error);
    }
}

/**
 * Finaliza la carta y la marca como lista
 */
async function finalizarCarta() {
    if (!plantillaSeleccionada) {
        alert('Selecciona una plantilla primero');
        return;
    }
    
    try {
        const nombreCarta = document.getElementById('nombreCarta').value.trim();
        if (!nombreCarta) {
            alert('Por favor, ingresa un nombre para la carta');
            return;
        }
        
        mostrarLoading(true, 'Finalizando carta...');
        
        // Guardar primero como borrador y obtener el ID
        const response = await axios.post('/personalizacion/canvas-editor/guardar_carta_temporal/', {
            plantilla_id: plantillaSeleccionada.id,
            nombre_carta: nombreCarta,
            parametros: elementosActuales
                .map(elemento => {
                    const input = document.getElementById(`param_${elemento.nombre_parametro}`);
                    return input?.value ? {
                        nombre_parametro: elemento.nombre_parametro,
                        tipo_parametro: elemento.tipo_elemento,
                        valor: input.value
                    } : null;
                })
                .filter(p => p !== null)
        });
        
        const cartaId = response.data?.carta_id;
        
        if (!cartaId) {
            throw new Error('No se pudo obtener el ID de la carta');
        }
        
        // Guardar las imágenes PNG
        await guardarImagenesCartas(cartaId);
        
        // Finalizar la carta
        await axios.post(`/personalizacion/finalizar-carta/${cartaId}/`, {});
        
        alert('¡Carta finalizada exitosamente!');
        window.location.href = '/personalizacion/mis-cartas/';
        
    } catch (error) {
        console.error('❌ Error finalizando carta:', error);
        const errorMsg = error.response?.data?.error || error.message || 'Error desconocido';
        alert(`Error al finalizar la carta: ${errorMsg}`);
    } finally {
        mostrarLoading(false);
    }
}

// ============================================================================
// CARGAR CARTA EXISTENTE
// ============================================================================

/**
 * Carga una carta existente para edición
 */
async function cargarCartaExistente(cartaId) {
    try {
        console.log('🔄 Cargando carta ID:', cartaId);
        mostrarLoading(true, 'Cargando carta...');
        
        const response = await axios.get(`/personalizacion/cartas/${cartaId}/`);
        const carta = response.data;
        
        console.log('✅ Carta cargada:', carta);
        
        if (!carta.plantilla_info?.id) {
            throw new Error('La carta no tiene información de plantilla válida');
        }
        
        window.cartaActual = carta;
        
        // Cargar nombre
        if (carta.nombre_carta) {
            document.getElementById('nombreCarta').value = carta.nombre_carta;
        }
        
        // Esperar plantillas y seleccionar
        await esperarPlantillasCargadas();
        await seleccionarPlantillaPorId(carta.plantilla_info.id);
        
        // Cargar parámetros
        if (carta.parametros?.length > 0) {
            await esperarControlesGenerados();
            cargarParametrosCarta(carta.parametros);
        }
        
        document.title = `Editando: ${carta.nombre_carta} - NM Collections`;
        console.log('✅ Carta cargada completamente');
        
    } catch (error) {
        console.error('❌ Error cargando carta:', error);
        alert('Error al cargar la carta. Intenta nuevamente.');
    } finally {
        mostrarLoading(false);
    }
}

/**
 * Espera a que las plantillas estén cargadas
 */
function esperarPlantillasCargadas() {
    return new Promise(resolve => {
        const verificar = () => {
            const container = document.getElementById('plantillasContainer');
            if (container?.children.length > 0) {
                resolve();
            } else {
                setTimeout(verificar, 200);
            }
        };
        verificar();
    });
}

/**
 * Selecciona una plantilla por su ID
 */
async function seleccionarPlantillaPorId(plantillaId) {
    const cards = document.querySelectorAll('.plantilla-card');
    for (let card of cards) {
        if (card.dataset.plantillaId == plantillaId) {
            card.click();
            return true;
        }
    }
    console.warn('⚠️ Plantilla no encontrada:', plantillaId);
    return false;
}

/**
 * Espera a que se generen los controles de elementos
 */
function esperarControlesGenerados() {
    return new Promise(resolve => {
        let intentos = 0;
        const verificar = () => {
            const inputs = document.querySelectorAll('#elementosContainer input, #elementosContainer select');
            if (inputs.length > 0 || intentos >= 20) {
                resolve();
            } else {
                intentos++;
                setTimeout(verificar, 500);
            }
        };
        verificar();
    });
}

/**
 * Carga los parámetros de una carta en los controles
 */
function cargarParametrosCarta(parametros) {
    let cargados = 0;
    
    parametros.forEach(param => {
        const input = document.getElementById(`param_${param.nombre_parametro}`);
        
        if (input) {
            if (input.type === 'file' && param.valor?.includes('/media/')) {
                cargarImagenDesdeURL(param.nombre_parametro, param.valor);
                cargados++;
            } else {
                input.value = param.valor;
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
                
                if (input.type === 'color') {
                    actualizarElemento(param.nombre_parametro, param.valor);
                }
                cargados++;
            }
        }
    });
    
    console.log(`✅ ${cargados}/${parametros.length} parámetros cargados`);
    canvas.renderAll();
}

// ============================================================================
// UTILIDADES
// ============================================================================

/**
 * Limpia el canvas y todos los inputs
 */
function limpiarCanvas() {
    if (!confirm('¿Estás seguro de limpiar el canvas?')) return;
    
    canvas.clear();
    canvas.setBackgroundColor('#ffffff', canvas.renderAll.bind(canvas));
    
    document.querySelectorAll('#elementosContainer input').forEach(input => {
        input.value = '';
    });
}

/**
 * Exporta la carta como imagen PNG
 */
function exportarImagen() {
    const dataURL = canvas.toDataURL('image/png');
    const link = document.createElement('a');
    link.download = `${document.getElementById('nombreCarta').value || 'trading_card'}.png`;
    link.href = dataURL;
    link.click();
}
