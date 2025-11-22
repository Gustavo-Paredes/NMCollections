from django.urls import path
from . import views
from .views_recuperacion import solicitar_recuperacion, restablecer_password

app_name = 'usuarios'

urlpatterns = [
    # Autenticación
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Recuperación de contraseña
    path('recuperar-password/', solicitar_recuperacion, name='solicitar_recuperacion'),
    path('restablecer-password/<uidb64>/<token>/', restablecer_password, name='restablecer_password'),
    
    # Dashboard y perfil
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    
    # Direcciones
    path('addresses/', views.addresses_view, name='addresses'),
    path('addresses/add/', views.add_address_view, name='add_address'),
    path('addresses/<int:address_id>/edit/', views.edit_address_view, name='edit_address'),
    path('addresses/<int:address_id>/delete/', views.delete_address_view, name='delete_address'),
]