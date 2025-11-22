from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.forms import modelformset_factory
from django.db import transaction
from django.db import models
from .models import Plantilla, PlantillaElemento, PlantillaFondo
from .forms import PlantillaForm, PlantillaElementoForm

def es_admin(user):
    """Verificar si el usuario es administrador o diseñador"""
    return user.is_authenticated and (
        user.is_superuser or 
        user.rol.nombre == 'Administrador' or 
        user.rol.nombre == 'Diseñador'
    )

@login_required
@user_passes_test(es_admin)
def panel_diseñador(request):
    """Panel principal para diseñadores"""
    plantillas = Plantilla.objects.all().order_by('-fecha_creacion')
    return render(request, 'personalizacion/panel_diseñador.html', {
        'plantillas': plantillas
    })

@login_required
@user_passes_test(es_admin)
def crear_plantilla(request):
    """Crear nueva plantilla con elementos"""
    if request.method == 'POST':
        form = PlantillaForm(request.POST, request.FILES)
        
        # Obtener elementos del formulario
        elementos_data = []
        elemento_count = int(request.POST.get('elemento_count', 0))
        
        for i in range(elemento_count):
            nombre = request.POST.get(f'elemento_{i}_nombre')
            tipo = request.POST.get(f'elemento_{i}_tipo')
            x = request.POST.get(f'elemento_{i}_x', 0)
            y = request.POST.get(f'elemento_{i}_y', 0)
            ancho = request.POST.get(f'elemento_{i}_ancho', 100)
            alto = request.POST.get(f'elemento_{i}_alto', 30)
            
            if nombre and tipo:
                elementos_data.append({
                    'nombre_parametro': nombre,
                    'tipo_elemento': tipo,
                    'posicion_x': int(x),
                    'posicion_y': int(y),
                    'ancho': int(ancho),
                    'alto': int(alto),
                    'z_index': i + 1
                })
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    plantilla = form.save(commit=False)
                    plantilla.usuario_creador = request.user
                    plantilla.save()
                    
                    # Crear elementos
                    for elemento_data in elementos_data:
                        PlantillaElemento.objects.create(
                            plantilla=plantilla,
                            **elemento_data
                        )
                    
                    messages.success(request, f'Plantilla "{plantilla.nombre}" creada exitosamente con {len(elementos_data)} elementos')
                    return redirect('personalizacion:editar_plantilla', plantilla_id=plantilla.id)
            except Exception as e:
                messages.error(request, f'Error al crear la plantilla: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario')
    else:
        form = PlantillaForm()
    
    return render(request, 'personalizacion/crear_plantilla.html', {
        'form': form
    })

@login_required
@user_passes_test(es_admin)
def editar_plantilla(request, plantilla_id):
    """Editar plantilla existente"""
    plantilla = get_object_or_404(Plantilla, id=plantilla_id)
    
    if request.method == 'POST':
        form = PlantillaForm(request.POST, request.FILES, instance=plantilla)
        if form.is_valid():
            form.save()
            messages.success(request, f'Plantilla "{plantilla.nombre}" actualizada exitosamente')
            return redirect('personalizacion:panel_diseñador')
    else:
        form = PlantillaForm(instance=plantilla)
    
    elementos = PlantillaElemento.objects.filter(plantilla=plantilla).order_by('z_index')
    
    return render(request, 'personalizacion/editar_plantilla.html', {
        'form': form,
        'plantilla': plantilla,
        'elementos': elementos
    })

@login_required
@user_passes_test(es_admin)
def eliminar_plantilla(request, plantilla_id):
    """Eliminar plantilla"""
    plantilla = get_object_or_404(Plantilla, id=plantilla_id)
    
    if request.method == 'POST':
        nombre = plantilla.nombre
        plantilla.delete()
        messages.success(request, f'Plantilla "{nombre}" eliminada exitosamente')
        return redirect('personalizacion:panel_diseñador')
    
    return render(request, 'personalizacion/confirmar_eliminar_plantilla.html', {
        'plantilla': plantilla
    })

@login_required
@user_passes_test(es_admin)
def agregar_elemento(request, plantilla_id):
    """Agregar elemento a plantilla"""
    plantilla = get_object_or_404(Plantilla, id=plantilla_id)
    
    if request.method == 'POST':
        form = PlantillaElementoForm(request.POST)
        if form.is_valid():
            elemento = form.save(commit=False)
            elemento.plantilla = plantilla
            # Asignar z_index automáticamente
            max_z = PlantillaElemento.objects.filter(plantilla=plantilla).aggregate(
                models.Max('z_index'))['z_index__max'] or 0
            elemento.z_index = max_z + 1
            elemento.save()
            messages.success(request, f'Elemento "{elemento.nombre_parametro}" agregado exitosamente')
            return redirect('personalizacion:editar_plantilla', plantilla_id=plantilla.id)
    else:
        form = PlantillaElementoForm()
    
    return render(request, 'personalizacion/agregar_elemento.html', {
        'form': form,
        'plantilla': plantilla
    })

@login_required
@user_passes_test(es_admin)
def eliminar_elemento(request, elemento_id):
    """Eliminar elemento de plantilla"""
    elemento = get_object_or_404(PlantillaElemento, id=elemento_id)
    plantilla_id = elemento.plantilla.id
    
    if request.method == 'POST':
        nombre = elemento.nombre_parametro
        elemento.delete()
        messages.success(request, f'Elemento "{nombre}" eliminado exitosamente')
        return redirect('personalizacion:editar_plantilla', plantilla_id=plantilla_id)
    
    return render(request, 'personalizacion/confirmar_eliminar_elemento.html', {
        'elemento': elemento
    })

@login_required
@user_passes_test(es_admin)
def cambiar_estado_plantilla(request, plantilla_id):
    """Cambiar estado de plantilla (activa/inactiva)"""
    if request.method == 'POST':
        plantilla = get_object_or_404(Plantilla, id=plantilla_id)
        plantilla.estado = 'inactiva' if plantilla.estado == 'activa' else 'activa'
        plantilla.save()
        
        estado_texto = 'activada' if plantilla.estado == 'activa' else 'desactivada'
        messages.success(request, f'Plantilla "{plantilla.nombre}" {estado_texto} exitosamente')
        
        return JsonResponse({
            'success': True,
            'nuevo_estado': plantilla.estado,
            'estado_texto': estado_texto
        })
    
    return JsonResponse({'success': False})