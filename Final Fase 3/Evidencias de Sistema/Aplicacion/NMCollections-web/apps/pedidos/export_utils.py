import csv
import io
import os
from decimal import Decimal, ROUND_HALF_UP
from django.http import HttpResponse
from apps.pedidos.models import Pedido
from django.utils.encoding import smart_str
from django.conf import settings

try:
    import openpyxl
except ImportError:
    openpyxl = None

try:
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.pdfgen import canvas
except ImportError:
    canvas = None

def _to_int_amount(value):
    """Convierte un monto Decimal/float/int a entero sin decimales (CLP)."""
    if value is None:
        return 0
    try:
        d = Decimal(str(value))
        return int(d.to_integral_value(rounding=ROUND_HALF_UP))
    except Exception:
        try:
            return int(round(float(value)))
        except Exception:
            return 0


def _user_name_and_email(usuario):
    """Retorna (nombre_completo, correo) con degradación segura."""
    nombre = None
    correo = None
    try:
        if hasattr(usuario, 'get_full_name') and callable(usuario.get_full_name):
            nombre = usuario.get_full_name()
        else:
            nombre = getattr(usuario, 'nombre', str(usuario))
        correo = getattr(usuario, 'correo', None) or getattr(usuario, 'email', '')
    except Exception:
        nombre = str(usuario)
        correo = ''
    return nombre, correo


def _is_loss(pedido):
    """Determina si un pedido debe contarse como pérdida.
    Reglas:
      - Si el estado del pedido es 'anulado' o 'devuelto'.
      - Si existe alguna transacción reembolsada o con reembolso completado.
    """
    try:
        estado = (pedido.estado or '').lower()
        if estado in { 'anulado', 'devuelto' }:
            return True
        # Reembolso por estado de transacción
        if hasattr(pedido, 'transacciones'):
            if pedido.transacciones.filter(estado='reembolsado').exists():
                return True
            # Reembolso explícito asociado
            if pedido.transacciones.filter(reembolsos__estado='completado').exists():
                return True
    except Exception:
        pass
    return False


def export_csv(pedidos):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="informe_ventas.csv"'
    writer = csv.writer(response)
    writer.writerow(["Informe de Ventas - NM Collections"])
    writer.writerow([""])
    writer.writerow(['Número de Pedido', 'Usuario', 'Correo', 'Fecha', 'Total', 'Estado', 'Método de Pago'])
    total_ganancias = 0
    total_perdidas = 0
    for pedido in pedidos:
        nombre, correo = _user_name_and_email(pedido.usuario)
        monto = _to_int_amount(pedido.total)
        if _is_loss(pedido):
            total_perdidas += monto
        else:
            total_ganancias += monto
        writer.writerow([
            pedido.numero_pedido,
            smart_str(nombre),
            smart_str(correo),
            pedido.fecha_pedido.strftime('%Y-%m-%d'),
            monto,
            pedido.estado,
            pedido.metodo_pago
        ])
    # Subtotales
    writer.writerow([""])
    writer.writerow(['Subtotal Pérdidas', total_perdidas])
    writer.writerow(['Subtotal Ganancias', total_ganancias])

    return response

def export_excel(pedidos):
    if not openpyxl:
        return HttpResponse('openpyxl no está instalado', status=500)
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.append(["Informe de Ventas - NM Collections"])
    ws.append([""])
    ws.append(['Número de Pedido', 'Usuario', 'Correo', 'Fecha', 'Total', 'Estado', 'Método de Pago'])
    total_ganancias = 0
    total_perdidas = 0
    for pedido in pedidos:
        nombre, correo = _user_name_and_email(pedido.usuario)
        monto = _to_int_amount(pedido.total)
        if _is_loss(pedido):
            total_perdidas += monto
        else:
            total_ganancias += monto
        ws.append([
            pedido.numero_pedido,
            str(nombre),
            str(correo),
            pedido.fecha_pedido.strftime('%Y-%m-%d'),
            monto,  # número entero para Excel
            pedido.estado,
            pedido.metodo_pago
        ])
    # Subtotales
    ws.append([""])
    ws.append(['Subtotal Pérdidas', total_perdidas])
    ws.append(['Subtotal Ganancias', total_ganancias])
    

    # Ajustar anchos de columnas para evitar textos cortados
    col_widths = {
        'A': 16,  # Número de Pedido
        'B': 28,  # Usuario
        'C': 25,  # Correo
        'D': 12,  # Fecha
        'E': 12,  # Total
        'F': 14,  # Estado
        'G': 20,  # Método de Pago
    }
    for col, width in col_widths.items():
        try:
            ws.column_dimensions[col].width = width
        except Exception:
            pass
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'inline; filename="informe_ventas.xlsx"'
    return response

def export_pdf(pedidos):
    if not canvas:
        return HttpResponse('reportlab no está instalado', status=500)
    buffer = io.BytesIO()
    # Usar orientación horizontal para más ancho útil
    p = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)
    y = height - 40
    p.setFont('Helvetica-Bold', 14)
    p.drawString(40, y, 'Informe de Ventas - NM Collections')
    y -= 30
    p.setFont('Helvetica', 10)

    headers = ['N° Pedido', 'Usuario', 'Correo', 'Fecha', 'Total', 'Estado', 'Método de Pago']

    # Cálculo de columnas: márgenes y anchos proporcionales
    left_margin = 20
    right_margin = 20
    available = width - left_margin - right_margin

    # Pesos relativos por columna (suman 1.0 aprox)
    weights = [0.12, 0.19, 0.20, 0.10, 0.10, 0.08, 0.15]
    col_widths = [available * w for w in weights]

    # Posiciones X por columna
    col_x = [left_margin]
    for w in col_widths[:-1]:
        col_x.append(col_x[-1] + w)

    # Helper para ajustar en una línea con "..." si excede el ancho
    def fit_text(txt, max_w, font='Helvetica', size=10):
        t = str(txt) if txt is not None else ''
        if p.stringWidth(t, font, size) <= max_w:
            return t
        ell = '...'
        ell_w = p.stringWidth(ell, font, size)
        lo, hi = 0, len(t)
        while lo < hi:
            mid = (lo + hi) // 2
            if p.stringWidth(t[:mid], font, size) + ell_w <= max_w:
                lo = mid + 1
            else:
                hi = mid
        cut = max(0, lo - 1)
        return t[:cut] + ell

    def draw_headers(y_top):
        p.setFont('Helvetica-Bold', 10)
        for i, h in enumerate(headers):
            p.drawString(col_x[i], y_top, fit_text(h, col_widths[i] - 4, 'Helvetica-Bold', 10))
        return y_top - 18

    # Dibujar cabeceras (una línea; si exceden, se acortan con ...)
    y = draw_headers(y)
    p.setFont('Helvetica', 9)

    row_height = 16
    bottom_margin = 40

    total_ganancias = 0
    total_perdidas = 0

    for pedido in pedidos:
        nombre, correo = _user_name_and_email(pedido.usuario)
        data = [
            pedido.numero_pedido,
            nombre,
            correo,
            pedido.fecha_pedido.strftime('%Y-%m-%d'),
            _to_int_amount(pedido.total),
            pedido.estado,
            pedido.metodo_pago,
        ]
        # Acumular subtotales
        monto = data[4]
        if _is_loss(pedido):
            total_perdidas += monto
        else:
            total_ganancias += monto

        if y - row_height < bottom_margin:
            p.showPage()
            # Reset para nueva página

            p.setFont('Helvetica-Bold', 14)
            p.drawString(40, height - 40, 'Informe de Ventas - NM Collections')
            p.setFont('Helvetica-Bold', 10)
            y = height - 70
            y = draw_headers(y)
            p.setFont('Helvetica', 9)

        # Dibujar fila en una línea por celda (acorta con ... si excede)
        for i, val in enumerate(data):
            p.drawString(col_x[i], y, fit_text(val, col_widths[i] - 4, 'Helvetica', 9))
        y -= row_height

    # Dibujar subtotales al final
    subtotal_labels = [
        ("Subtotal Pérdidas", total_perdidas),
        ("Subtotal Ganancias", total_ganancias),
        
    ]
    p.setFont('Helvetica-Bold', 11)
    # Intentar alinear bajo la columna Total (índice 4)
    label_x = col_x[0]
    value_x = col_x[4]  # columna Total
    needed_height = len(subtotal_labels) * 18
    if y - needed_height < bottom_margin:
        p.showPage()
        p.setFont('Helvetica-Bold', 14)
        p.drawString(40, height - 40, 'Informe de Ventas - NM Collections')
        p.setFont('Helvetica', 9)
        y = height - 70
    for label, value in subtotal_labels:
        p.drawString(label_x, y, str(label))
        p.drawString(value_x, y, str(value))
        y -= 18
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="informe_ventas.pdf"'
    return response
