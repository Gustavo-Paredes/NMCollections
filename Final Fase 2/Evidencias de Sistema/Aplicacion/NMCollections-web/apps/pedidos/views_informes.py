from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.utils.encoding import smart_str
from apps.pedidos.models import Pedido
from .export_utils import export_csv, export_excel, export_pdf

@staff_member_required
def descargar_informe_ventas(request):
    pedidos = Pedido.objects.all().order_by('-fecha_pedido')
    return export_csv(pedidos)

@staff_member_required
def descargar_informe_ventas_excel(request):
    pedidos = Pedido.objects.all().order_by('-fecha_pedido')
    return export_excel(pedidos)

@staff_member_required
def descargar_informe_ventas_pdf(request):
    pedidos = Pedido.objects.all().order_by('-fecha_pedido')
    return export_pdf(pedidos)
