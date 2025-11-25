from decimal import Decimal, InvalidOperation
from django import template

register = template.Library()


def _to_decimal(value):
    """Convierte un valor a Decimal de forma segura"""
    if value is None:
        return Decimal(0)
    try:
        if isinstance(value, Decimal):
            return value
        # Allow ints, floats, and numeric strings
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(0)


@register.filter(name="miles")
def miles(value, decimals=0):
    """
    Formatea un número con separador de miles estilo español (punto) y coma decimal.
    Ejemplos:
      1234 -> "1.234"
      1234.5, decimals=2 -> "1.234,50"
    
    Args:
        value: Número a formatear (int, float, Decimal, str)
        decimals: Cantidad de decimales a mostrar (default: 0)
    
    Returns:
        String formateado con separador de miles
    """
    dec = 0
    try:
        dec = int(decimals)
    except (ValueError, TypeError):
        dec = 0

    num = _to_decimal(value)

    # Formato base con separador de miles norteamericano: 12,345.67
    fmt = f"{{:,.{dec}f}}".format(num)
    
    # Convertir a formato español: 12.345,67
    # Paso temporal para evitar colisiones en reemplazo
    fmt = fmt.replace(",", "_")  # 12_345.67
    fmt = fmt.replace(".", ",")   # 12_345,67
    fmt = fmt.replace("_", ".")  # 12.345,67
    
    return fmt


# Alias adicional por si acaso
@register.filter(name="format_miles")
def format_miles(value, decimals=0):
    """Alias del filtro miles"""
    return miles(value, decimals)


# Filtro simple para testing
@register.filter(name="format_number")
def format_number(value):
    """Formatea número con separador de miles simple"""
    try:
        num = float(value)
        return f"{num:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return value
