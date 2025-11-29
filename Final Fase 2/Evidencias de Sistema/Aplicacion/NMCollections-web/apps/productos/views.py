from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from .models import Producto, CategoriaProducto, ImagenProducto


class ProductoListView(ListView):
    model = Producto
    template_name = 'productos/catalogo.html'
    context_object_name = 'productos'
    paginate_by = 24

    def get_queryset(self):
        # Mostrar sólo productos disponibles: activos y con stock > 0 (o sin stock definido) o digitales
        # Excluir productos tipo personalizado
        return (
            Producto.objects
            .filter(
                Q(estado='activo') & ~Q(tipo='personalizado') & (Q(tipo='digital') | Q(stock__isnull=True) | Q(stock__gt=0))
            )
            .select_related('categoria')
            .prefetch_related('imagenes')
        )


class ProductoDetalleView(DetailView):
    model = Producto
    template_name = 'productos/producto_detalle.html'
    context_object_name = 'producto'
    pk_url_kwarg = 'producto_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Construir galería sin duplicados: usar imagen principal si existe,
        # en caso contrario usar la primera imagen adicional como principal
        producto = self.object

        # URL de imagen principal
        principal_url = ''
        # URLs de imágenes adicionales
        extras_urls = []

        # Intentar usar imagen_referencia como principal
        if producto.imagen_referencia:
            try:
                principal_url = producto.imagen_referencia.url
            except Exception:
                principal_url = ''

        # Obtener imágenes adicionales ordenadas
        imagenes_qs = producto.imagenes.all().order_by('-es_principal', 'orden', 'id')

        if not principal_url:
            # Si no hay imagen principal en el producto, usar la primera adicional (si existe)
            primera = imagenes_qs.first()
            if primera:
                try:
                    principal_url = primera.imagen.url
                except Exception:
                    principal_url = ''
                # El resto como extras (excluyendo la primera)
                for img in imagenes_qs[1:]:
                    try:
                        extras_urls.append(img.imagen.url)
                    except Exception:
                        continue
            else:
                extras_urls = []
        else:
            # Hay imagen principal en el producto; todas las adicionales son extras
            for img in imagenes_qs:
                try:
                    extras_urls.append(img.imagen.url)
                except Exception:
                    continue

        context['imagen_principal_url'] = principal_url
        context['imagenes_extras_urls'] = extras_urls
        return context


def home(request):
    """Función simple que renderiza el catálogo (misma salida que ProductoListView)."""
    productos = (
        Producto.objects
        .filter(Q(estado='activo') & ~Q(tipo='personalizado') & (Q(tipo='digital') | Q(stock__isnull=True) | Q(stock__gt=0)))
        .select_related('categoria')
    )
    return render(request, 'productos/catalogo.html', {
        'title': 'Catálogo - NM Collections',
        'productos': productos,
    })


class GestionarProductosView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Producto
    template_name = 'productos/gestionar_productos.html'
    context_object_name = 'productos'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        categoria = self.request.GET.get('categoria')
        estado = self.request.GET.get('estado')
        
        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q) |
                Q(descripcion__icontains=q)
            )
        if categoria:
            queryset = queryset.filter(categoria_id=categoria)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset.select_related('categoria').prefetch_related('imagenes')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = CategoriaProducto.objects.all()
        return context


class CrearProductoView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Producto
    fields = ['nombre', 'descripcion', 'categoria', 'precio_base', 'stock', 'tipo', 'estado', 'imagen_referencia']
    success_url = reverse_lazy('productos:gestionar')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Procesar imágenes adicionales
        imagenes = self.request.FILES.getlist('imagenes_adicionales')
        nuevas = []
        for idx, imagen in enumerate(imagenes):
            nuevas.append(ImagenProducto(
                producto=self.object,
                imagen=imagen,
                alt_text=f"{self.object.nombre} - Imagen {idx + 1}",
                orden=idx
            ))
        if nuevas:
            # Guardar en bulk para eficiencia
            ImagenProducto.objects.bulk_create(nuevas)
            # Si no hay imagen principal definida, marcar la primera adicional como principal
            if not self.object.imagen_referencia:
                primera = self.object.imagenes.order_by('orden', 'id').first()
                if primera and not primera.es_principal:
                    primera.es_principal = True
                    primera.save(update_fields=['es_principal'])
        messages.success(self.request, f'Producto creado exitosamente con {len(imagenes)} imagen(es) adicional(es).')
        return response


class EditarProductoView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Producto
    fields = ['nombre', 'descripcion', 'categoria', 'precio_base', 'stock', 'tipo', 'estado', 'imagen_referencia']
    success_url = reverse_lazy('productos:gestionar')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasar las imágenes actuales para mostrarlas
        context['imagenes_actuales'] = self.object.imagenes.all()
        return context
    
    def form_valid(self, form):
        # Verificar si se solicitó eliminar la imagen principal
        if self.request.POST.get('eliminar_imagen'):
            # Eliminar archivo físico si existe y luego limpiar el campo
            if form.instance.imagen_referencia:
                try:
                    form.instance.imagen_referencia.delete(save=False)
                except Exception:
                    pass
            form.instance.imagen_referencia = None
        
        response = super().form_valid(form)
        
        # Procesar imágenes adicionales nuevas
        imagenes = self.request.FILES.getlist('imagenes_adicionales')
        ultimo_orden = self.object.imagenes.count()
        nuevas = []
        for idx, imagen in enumerate(imagenes):
            nuevas.append(ImagenProducto(
                producto=self.object,
                imagen=imagen,
                alt_text=f"{self.object.nombre} - Imagen {ultimo_orden + idx + 1}",
                orden=ultimo_orden + idx
            ))
        if nuevas:
            ImagenProducto.objects.bulk_create(nuevas)
            # Si no hay principal (ni imagen_referencia ni imagen principal marcada), marcar la primera nueva
            if not self.object.imagen_referencia and not self.object.imagenes.filter(es_principal=True).exists():
                primera = self.object.imagenes.order_by('orden', 'id').first()
                if primera:
                    primera.es_principal = True
                    primera.save(update_fields=['es_principal'])
        
        # Procesar eliminación de imágenes adicionales
        imagenes_eliminar = self.request.POST.getlist('eliminar_imagen_adicional')
        if imagenes_eliminar:
            ImagenProducto.objects.filter(id__in=imagenes_eliminar).delete()
        
        msg = f'Producto actualizado exitosamente'
        if imagenes:
            msg += f' con {len(imagenes)} imagen(es) adicional(es)'
        if imagenes_eliminar:
            msg += f'. Se eliminaron {len(imagenes_eliminar)} imagen(es)'
        messages.success(self.request, msg + '.')
        
        return response


class EliminarProductoView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Producto
    success_url = reverse_lazy('productos:gestionar')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        # Respuesta para peticiones AJAX (fetch) sin recargar página
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'id': self.object.pk})
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect(self.success_url)


class ProductoAPIView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff
    
    def get(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        
        # Convertir ImageFieldFile a URL o string vacío
        imagen_url = ''
        if producto.imagen_referencia:
            try:
                imagen_url = producto.imagen_referencia.url
            except:
                imagen_url = str(producto.imagen_referencia) if producto.imagen_referencia else ''
        
        return JsonResponse({
            'id': producto.id,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'categoria': producto.categoria_id,
            'precio_base': str(producto.precio_base),
            'stock': producto.stock,
            'tipo': producto.tipo,
            'estado': producto.estado,
            'imagen_referencia': imagen_url,
        })
