from rest_framework import permissions


class IsAdminRole(permissions.BasePermission):
    """Permite acceso solo a usuarios autenticados con rol ADMIN o is_staff."""

    message = "Se requiere rol de administrador para realizar esta acción."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.role == 'ADMIN' or user.is_staff)
        )


class IsSellerOrAdmin(permissions.BasePermission):
    """Permite lectura pública y escritura solo a vendedores o administradores."""

    message = "Solo vendedores o administradores pueden realizar esta acción."

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.role in ('SELLER', 'ADMIN') or user.is_staff)
        )


class IsProductOwnerOrAdmin(permissions.BasePermission):
    """Permite modificar o eliminar un producto solo a su vendedor dueño o a un admin."""

    message = "Solo puedes modificar o eliminar tus propios productos."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.role == 'ADMIN' or user.is_staff:
            return True
        return user.role == 'SELLER' and obj.seller_id == user.id
