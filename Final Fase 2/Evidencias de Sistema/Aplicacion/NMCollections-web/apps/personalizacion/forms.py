from django import forms
from .models import Plantilla, PlantillaElemento, PlantillaFondo

class PlantillaForm(forms.ModelForm):
    class Meta:
        model = Plantilla
        fields = [
            'nombre', 'descripcion', 'tipo_carta', 'imagen_marco', 
            'ancho_marco', 'alto_marco', 'diseñador', 'estado'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la plantilla'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la plantilla'
            }),
            'tipo_carta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Pokémon, Yu-Gi-Oh!, Magic'
            }),
            'imagen_marco': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'ancho_marco': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '100',
                'max': '1000'
            }),
            'alto_marco': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '100',
                'max': '1000'
            }),
            'diseñador': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del diseñador'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control'
            })
        }

class PlantillaElementoForm(forms.ModelForm):
    class Meta:
        model = PlantillaElemento
        fields = [
            'nombre_parametro', 'tipo_elemento', 'posicion_x', 'posicion_y',
            'ancho', 'alto', 'fuente', 'color'
        ]
        FONT_CHOICES = [
            ('Arial', 'Arial'),
            ('Roboto', 'Roboto'),
            ('Times New Roman', 'Times New Roman'),
            ('Comic Sans MS', 'Comic Sans MS'),
            ('Courier New', 'Courier New'),
            ('Georgia', 'Georgia'),
            ('Impact', 'Impact'),
            ('Tahoma', 'Tahoma'),
            ('Trebuchet MS', 'Trebuchet MS'),
            ('Verdana', 'Verdana'),
        ]
        widgets = {
            'nombre_parametro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: nombre_pokemon, ataque, hp'
            }),
            'tipo_elemento': forms.Select(attrs={
                'class': 'form-control'
            }),
            'posicion_x': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'posicion_y': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'ancho': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'alto': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'fuente': forms.Select(choices=FONT_CHOICES, attrs={'class': 'form-control font-preview'}),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            })
        }

class PlantillaFondoForm(forms.ModelForm):
    class Meta:
        model = PlantillaFondo
        fields = ['tipo_fondo', 'valor']
        widgets = {
            'tipo_fondo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'valor': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Color hex, URL de imagen o gradiente CSS'
            })
        }