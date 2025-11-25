from django import forms
from .models import Subasta
from django.utils import timezone
from datetime import datetime

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
            'precio_reserva',
        ]

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio_fecha')
        fecha_fin = cleaned_data.get('fecha_fin_fecha')
        hora_inicio = cleaned_data.get('fecha_inicio_hora')
        hora_fin = cleaned_data.get('fecha_fin_hora')

        hoy = timezone.now().date()

        # Validar que la fecha de inicio sea hoy o posterior
        if fecha_inicio and fecha_inicio < hoy:
            self.add_error('fecha_inicio_fecha', 'La fecha de inicio debe ser hoy o posterior.')

        # Combinar fecha y hora y validar que el fin sea posterior al inicio
        if fecha_inicio and fecha_fin and hora_inicio and hora_fin:
            inicio = datetime.combine(fecha_inicio, hora_inicio)
            fin = datetime.combine(fecha_fin, hora_fin)
            if fin <= inicio:
                self.add_error('fecha_fin_fecha', 'La fecha y hora de fin deben ser posteriores a la de inicio.')
            else:
                cleaned_data['fecha_inicio'] = inicio
                cleaned_data['fecha_fin'] = fin

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.fecha_inicio = self.cleaned_data['fecha_inicio']
        instance.fecha_fin = self.cleaned_data['fecha_fin']
        if commit:
            instance.save()
        return instance
