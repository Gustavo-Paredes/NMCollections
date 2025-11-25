from rest_framework.decorators import api_view, permission_classes, schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Endpoint API para reportes admin
@swagger_auto_schema(
    method='get',
    operation_description="Reportes admin: métricas, ventas por mes, pedidos por estado y ventas por método de pago.",
    responses={200: openapi.Response('Reporte', examples={
        'application/json': {
            'metrics': {'total_ventas': 10000, 'total_pedidos': 20, 'pedidos_confirmados': 15},
            'ventas_por_mes': [1000, 2000, 3000],
            'labels_ventas_mes': ['Nov 2024', 'Dec 2024', 'Jan 2025'],
            'pedidos_estado_labels': ['pendiente', 'confirmado'],
            'pedidos_estado_values': [5, 15],
            'ventas_metodo_labels': ['WebPay', 'Transferencia'],
            'ventas_metodo_values': [7000, 3000],
        }
    })}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def reportes_admin_api(request):
    metrics = get_ventas_metrics()
    now = timezone.now()
    meses = [(now.replace(day=1) - timezone.timedelta(days=30*i)).strftime('%Y-%m') for i in range(11, -1, -1)]
    ventas_por_mes = OrderedDict((m, 0) for m in meses)
    for p in Pedido.objects.filter(fecha_pedido__gte=now.replace(year=now.year-1)).order_by('fecha_pedido'):
        mes = p.fecha_pedido.strftime('%Y-%m')
        if mes in ventas_por_mes:
            ventas_por_mes[mes] += float(p.total or 0)

    estados = dict(Pedido._meta.get_field('estado').choices)
    pedidos_estado = Pedido.objects.values('estado').annotate(c=Count('id'))
    pedidos_por_estado = {estados.get(e['estado'], e['estado']): e['c'] for e in pedidos_estado}

    metodos = Pedido.objects.values_list('metodo_pago', flat=True).distinct()
    ventas_metodo = {m: 0 for m in metodos if m}
    for p in Pedido.objects.all():
        if p.metodo_pago:
            ventas_metodo[p.metodo_pago] = ventas_metodo.get(p.metodo_pago, 0) + float(p.total or 0)

    return Response({
        'metrics': metrics,
        'ventas_por_mes': list(ventas_por_mes.values()),
        'labels_ventas_mes': [calendar.month_abbr[int(m.split('-')[1])] + ' ' + m.split('-')[0] for m in ventas_por_mes.keys()],
        'pedidos_estado_labels': list(pedidos_por_estado.keys()),
        'pedidos_estado_values': list(pedidos_por_estado.values()),
        'ventas_metodo_labels': list(ventas_metodo.keys()),
        'ventas_metodo_values': list(ventas_metodo.values()),
    })
    metrics = get_ventas_metrics()
    now = timezone.now()
    meses = [(now.replace(day=1) - timezone.timedelta(days=30*i)).strftime('%Y-%m') for i in range(11, -1, -1)]
    ventas_por_mes = OrderedDict((m, 0) for m in meses)
    for p in Pedido.objects.filter(fecha_pedido__gte=now.replace(year=now.year-1)).order_by('fecha_pedido'):
        mes = p.fecha_pedido.strftime('%Y-%m')
        if mes in ventas_por_mes:
            ventas_por_mes[mes] += float(p.total or 0)

    estados = dict(Pedido._meta.get_field('estado').choices)
    pedidos_estado = Pedido.objects.values('estado').annotate(c=Count('id'))
    pedidos_por_estado = {estados.get(e['estado'], e['estado']): e['c'] for e in pedidos_estado}

    metodos = Pedido.objects.values_list('metodo_pago', flat=True).distinct()
    ventas_metodo = {m: 0 for m in metodos if m}
    for p in Pedido.objects.all():
        if p.metodo_pago:
            ventas_metodo[p.metodo_pago] = ventas_metodo.get(p.metodo_pago, 0) + float(p.total or 0)

    return JsonResponse({
        'metrics': metrics,
        'ventas_por_mes': list(ventas_por_mes.values()),
        'labels_ventas_mes': [calendar.month_abbr[int(m.split('-')[1])] + ' ' + m.split('-')[0] for m in ventas_por_mes.keys()],
        'pedidos_estado_labels': list(pedidos_por_estado.keys()),
        'pedidos_estado_values': list(pedidos_por_estado.values()),
        'ventas_metodo_labels': list(ventas_metodo.keys()),
        'ventas_metodo_values': list(ventas_metodo.values()),
    })
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.urls import reverse
from apps.pedidos.models import Pedido
from django.db.models import Sum, Count

from django.utils import timezone
from collections import OrderedDict
import calendar

def get_ventas_metrics():
    total_ventas = Pedido.objects.aggregate(total=Sum('total'))['total'] or 0
    total_pedidos = Pedido.objects.count()
    pedidos_confirmados = Pedido.objects.filter(estado='confirmado').count()
    return {
        'total_ventas': total_ventas,
        'total_pedidos': total_pedidos,
        'pedidos_confirmados': pedidos_confirmados,
    }

@staff_member_required
def reportes_admin(request):
    metrics = get_ventas_metrics()
    url_csv = reverse('pedidos:informe_ventas')
    url_excel = reverse('pedidos:informe_ventas_excel')
    url_pdf = reverse('pedidos:informe_ventas_pdf')

    # Ventas por mes (últimos 12 meses)
    now = timezone.now()
    meses = [(now.replace(day=1) - timezone.timedelta(days=30*i)).strftime('%Y-%m') for i in range(11, -1, -1)]
    ventas_por_mes = OrderedDict((m, 0) for m in meses)
    for p in Pedido.objects.filter(fecha_pedido__gte=now.replace(year=now.year-1)).order_by('fecha_pedido'):
        mes = p.fecha_pedido.strftime('%Y-%m')
        if mes in ventas_por_mes:
            ventas_por_mes[mes] += float(p.total or 0)

    # Pedidos por estado
    estados = dict(Pedido._meta.get_field('estado').choices)
    pedidos_estado = Pedido.objects.values('estado').annotate(c=Count('id'))
    pedidos_por_estado = {estados.get(e['estado'], e['estado']): e['c'] for e in pedidos_estado}

    # Ventas por método de pago
    metodos = Pedido.objects.values_list('metodo_pago', flat=True).distinct()
    ventas_metodo = {m: 0 for m in metodos if m}
    for p in Pedido.objects.all():
        if p.metodo_pago:
            ventas_metodo[p.metodo_pago] = ventas_metodo.get(p.metodo_pago, 0) + float(p.total or 0)
    return render(request, 'admin/reportes_admin.html', {
        'metrics': metrics,
        'url_csv': url_csv,
        'url_excel': url_excel,
        'url_pdf': url_pdf,
        'ventas_por_mes': list(ventas_por_mes.values()),
        'labels_ventas_mes': [calendar.month_abbr[int(m.split('-')[1])] + ' ' + m.split('-')[0] for m in ventas_por_mes.keys()],
        'pedidos_estado_labels': list(pedidos_por_estado.keys()),
        'pedidos_estado_values': list(pedidos_por_estado.values()),
        'ventas_metodo_labels': list(ventas_metodo.keys()),
        'ventas_metodo_values': list(ventas_metodo.values()),
    })
