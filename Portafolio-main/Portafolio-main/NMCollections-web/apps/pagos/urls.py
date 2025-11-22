from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    # WebPay Plus
    path('webpay/retorno/', views.webpay_retorno, name='webpay_retorno'),
    
    # Páginas de resultado de pago
    path('pago/success/', views.pago_success, name='pago_success'),
    path('pago/failure/', views.pago_failure, name='pago_failure'),
]
