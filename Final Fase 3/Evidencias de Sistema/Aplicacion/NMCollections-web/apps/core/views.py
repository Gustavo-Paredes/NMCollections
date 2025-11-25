from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from apps.core.models import NFC

class HomeView(TemplateView):
    """Vista principal de la página de inicio"""
    template_name = 'index_converted.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'NM Collections - Inicio'
        return context

def home(request):
    """Vista de función simple para la página de inicio"""
    return render(request, 'home/index.html', {
        'title': 'Inicio - NM Collections'
    })

def nfc_detail(request, codigo_nfc):
    nfc = get_object_or_404(NFC, codigo_nfc=codigo_nfc)
    return render(request, 'NFC/nfc_detail.html', {'nfc': nfc})