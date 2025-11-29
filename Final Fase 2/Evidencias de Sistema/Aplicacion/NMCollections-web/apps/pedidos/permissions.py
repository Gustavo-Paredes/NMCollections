from rest_framework import permissions

class IsAdminOrDesigner(permissions.BasePermission):
    """
    Permite acceso solo a usuarios con rol admin o diseñador.
    Asume que el modelo User tiene un campo 'rol' (5 = diseñador, 1 = admin).
    """
    def has_permission(self, request, view):
        user = request.user
        # Permitir admin
        if user.is_staff:
            return True
        # Permitir diseñador (rol.id == 5)
        rol = getattr(user, 'rol', None)
        if hasattr(rol, 'id') and rol.id == 5:
            return True
        return False
