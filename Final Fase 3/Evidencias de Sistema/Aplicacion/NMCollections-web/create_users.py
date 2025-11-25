#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nmcollections.settings')
django.setup()

from apps.usuarios.models import Usuario, Rol

print("🚀 Inicializando usuarios del sistema NM Collections...")

# Crear rol de administrador si no existe
rol_admin, created = Rol.objects.get_or_create(
    nombre='Administrador',
    defaults={
        'descripcion': 'Rol con todos los permisos del sistema'
    }
)

if created:
    print("✓ Rol 'Administrador' creado")
else:
    print("✓ Rol 'Administrador' ya existe")

# Crear rol de cliente si no existe
rol_cliente, created = Rol.objects.get_or_create(
    nombre='Cliente',
    defaults={
        'descripcion': 'Usuario cliente estándar del sistema'
    }
)

if created:
    print("✓ Rol 'Cliente' creado")
else:
    print("✓ Rol 'Cliente' ya existe")

# Crear rol de diseñador si no existe
rol_disenador, created = Rol.objects.get_or_create(
    nombre='Diseñador',
    defaults={
        'descripcion': 'Usuario diseñador con acceso al canvas editor y creación de plantillas'
    }
)

if created:
    print("✓ Rol 'Diseñador' creado")
else:
    print("✓ Rol 'Diseñador' ya existe")

# Crear superusuario administrador si no existe
if not Usuario.objects.filter(correo='admin@nmcollections.com').exists():
    admin_user = Usuario.objects.create_superuser(
        username='admin',
        correo='admin@nmcollections.com',
        password='admin123',
        nombre='Admin',
        apellido_paterno='Sistema',
        rol=rol_admin
    )
    print("✓ Superusuario Admin creado:")
    print(f"  - Usuario: admin")
    print(f"  - Email: admin@nmcollections.com")
    print(f"  - Password: admin123")
else:
    print("✓ Superusuario Admin ya existe")

# Crear usuario cliente de ejemplo si no existe
if not Usuario.objects.filter(correo='cliente@nmcollections.com').exists():
    cliente_user = Usuario.objects.create_user(
        username='cliente',
        correo='cliente@nmcollections.com',
        password='cliente123',
        nombre='Cliente',
        apellido_paterno='Ejemplo',
        rol=rol_cliente
    )
    print("✓ Usuario Cliente creado:")
    print(f"  - Usuario: cliente")
    print(f"  - Email: cliente@nmcollections.com")
    print(f"  - Password: cliente123")
else:
    print("✓ Usuario Cliente ya existe")

# Crear usuario diseñador de ejemplo si no existe
if not Usuario.objects.filter(correo='disenador@nmcollections.com').exists():
    disenador_user = Usuario.objects.create_user(
        username='disenador',
        correo='disenador@nmcollections.com',
        password='disenador123',
        nombre='Diseñador',
        apellido_paterno='Creativo',
        rol=rol_disenador
    )
    print("✓ Usuario Diseñador creado:")
    print(f"  - Usuario: disenador")
    print(f"  - Email: disenador@nmcollections.com")
    print(f"  - Password: disenador123")
else:
    print("✓ Usuario Diseñador ya existe")

print("\n📋 Usuarios del sistema:")
print("┌─────────────┬──────────────────────────────┬─────────────┬─────────────────┐")
print("│ Usuario     │ Email                        │ Rol         │ Password        │")
print("├─────────────┼──────────────────────────────┼─────────────┼─────────────────┤")
print("│ admin       │ admin@nmcollections.com      │ Admin       │ admin123        │")
print("│ cliente     │ cliente@nmcollections.com    │ Cliente     │ cliente123      │")
print("│ disenador   │ disenador@nmcollections.com  │ Diseñador   │ disenador123    │")
print("└─────────────┴──────────────────────────────┴─────────────┴─────────────────┘")
print("\n✅ ¡Todos los usuarios base han sido creados automáticamente!")
print("🔗 Accede al admin: http://localhost:8004/admin/ (admin/admin123)")
print("🎨 Canvas Editor: http://localhost:8004/personalizacion/canvas-editor/ (disenador/disenador123)")


