from django.shortcuts import render

# Funcion para renderizar la plantilla home.html
def home(request):
        return render(request, 'inicio/index.html')

