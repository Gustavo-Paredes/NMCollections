# Generated manually for imagen_generada field

from django.db import migrations, models
import apps.personalizacion.models


class Migration(migrations.Migration):

    dependencies = [
        ('personalizacion', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartapersonalizada',
            name='fecha_actualizacion',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='cartapersonalizada',
            name='imagen_generada',
            field=models.ImageField(blank=True, help_text='Imagen PNG generada del canvas de la carta', null=True, upload_to=apps.personalizacion.models.carta_imagen_path),
        ),
    ]