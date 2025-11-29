from django import forms
from .models import Subasta
from django.utils import timezone
from datetime import datetime, timedelta
import traceback
import sys

class SubastaForm(forms.ModelForm):
    fecha_inicio_fecha = forms.DateField(
        label='Fecha de inicio',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().date()
    )
    fecha_inicio_hora = forms.TimeField(
        label='Hora de inicio',
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        initial=timezone.now().strftime('%H:%M')
    )
    fecha_fin_fecha = forms.DateField(
        label='Fecha de fin',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().date()
    )
    fecha_fin_hora = forms.TimeField(
        label='Hora de fin',
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        initial=timezone.now().strftime('%H:%M')
    )

    nombre_producto = forms.CharField(
        label='Nombre del producto (opcional)',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Subasta
        fields = [
            'producto',
            'nombre_producto',
            'precio_inicial',
            'incremento_minimo',
        ]

    def __init__(self, *args, **kwargs):
        # Permite inicializar campos de fecha/hora cuando se edita una instancia
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        # Si no es edición (creación) y no hay datos POST, establecer iniciales dinámicos
        if not instance and not self.data:
            ahora = timezone.now()
            fin = ahora + timedelta(hours=1)
            self.fields['fecha_inicio_fecha'].initial = ahora.date()
            self.fields['fecha_inicio_hora'].initial = ahora.strftime('%H:%M')
            self.fields['fecha_fin_fecha'].initial = fin.date()
            self.fields['fecha_fin_hora'].initial = fin.strftime('%H:%M')

        if instance:
            # Poblar campos fecha/hora desde la instancia (convertir a hora local)
            if instance.fecha_inicio:
                inicio_local = timezone.localtime(instance.fecha_inicio)
                self.fields['fecha_inicio_fecha'].initial = inicio_local.date()
                self.fields['fecha_inicio_hora'].initial = inicio_local.strftime('%H:%M')
            if instance.fecha_fin:
                fin_local = timezone.localtime(instance.fecha_fin)
                self.fields['fecha_fin_fecha'].initial = fin_local.date()
                self.fields['fecha_fin_hora'].initial = fin_local.strftime('%H:%M')
            # Nombre producto si existe
            if instance.producto:
                self.fields['nombre_producto'].initial = ''

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio_fecha')
        fecha_fin = cleaned_data.get('fecha_fin_fecha')
        hora_inicio = cleaned_data.get('fecha_inicio_hora')
        hora_fin = cleaned_data.get('fecha_fin_hora')

<<<<<<< Updated upstream
        # Usar localdate() para respetar la zona horaria configurada en Django
        from django.utils import timezone as _tz
        hoy = _tz.localdate()
        
        # Validar que la fecha de inicio sea hoy o posterior (solo para nuevas subastas)
        if not self.instance.pk and fecha_inicio and fecha_inicio < hoy:
            self.add_error('fecha_inicio_fecha', 'La fecha de inicio debe ser hoy o posterior.')
=======
        # Usar zona horaria local de Django
        hoy = timezone.localdate()  # Más robusto que timezone.now().date()

        # Validar que la fecha de inicio sea hoy o posterior
        if fecha_inicio and fecha_inicio < hoy:
            self.add_error('fecha_inicio_fecha', f'La fecha de inicio debe ser hoy ({hoy}) o posterior.')
>>>>>>> Stashed changes

        # Combinar fecha y hora y validar que el fin sea posterior al inicio
        if fecha_inicio and fecha_fin and hora_inicio and hora_fin:
            inicio = datetime.combine(fecha_inicio, hora_inicio)
            fin = datetime.combine(fecha_fin, hora_fin)
            
            # Hacerlos timezone-aware
            inicio = _tz.make_aware(inicio)
            fin = _tz.make_aware(fin)
            
            if fin <= inicio:
                self.add_error('fecha_fin_fecha', 'La fecha y hora de fin deben ser posteriores a la de inicio.')
            else:
                cleaned_data['fecha_inicio'] = inicio
                cleaned_data['fecha_fin'] = fin

        return cleaned_data

    def save(self, commit=True):
        try:
            instance = super().save(commit=False)
            instance.fecha_inicio = self.cleaned_data['fecha_inicio']
            instance.fecha_fin = self.cleaned_data['fecha_fin']
        except Exception as e:
            print("[DEBUG][SubastaForm.save] Error al preparar instancia:", file=sys.stderr)
            traceback.print_exc()
            raise
        # Si no se suministró un producto pero sí un nombre, crear producto mínimo
        if not instance.producto and self.cleaned_data.get('nombre_producto'):
            try:
                from apps.productos.models import CategoriaProducto, Producto
                categoria, _ = CategoriaProducto.objects.get_or_create(
                    nombre='Subastas',
                    defaults={'descripcion': 'Productos creados automáticamente para subastas'}
                )
                producto = Producto.objects.create(
                    nombre=self.cleaned_data.get('nombre_producto'),
                    descripcion=f'Producto creado automáticamente para la subasta "{self.cleaned_data.get("nombre_producto")}"',
                    precio_base=self.cleaned_data.get('precio_inicial') or 0,
                    categoria=categoria,
                    tipo='estandar',
                    estado='activo'
                )
                instance.producto = producto
            except Exception:
                print("[DEBUG][SubastaForm.save] Error creando Producto automático:", file=sys.stderr)
                traceback.print_exc()
                # re-raise para que la vista capture el error o la validación lo muestre
                raise

        if commit:
            try:
                instance.save()
            except Exception:
                print("[DEBUG][SubastaForm.save] Error al guardar instancia Subasta:", file=sys.stderr)
                traceback.print_exc()
                raise
        return instance
