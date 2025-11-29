"""Migration to add imagen_pedido field to PedidoProducto"""
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('pedidos', '0004_pedido_subasta'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedidoproducto',
            name='imagen_pedido',
            field=models.ImageField(blank=True, null=True, upload_to='pedidos/', verbose_name='Imagen del pedido', help_text='Snapshot de la imagen (producto o carta personalizada) en el momento de la compra'),
        ),
    ]