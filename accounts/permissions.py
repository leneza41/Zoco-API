"""
Reglas de permisos de la API, todas en este archivo para que sea fácil saber quién puede qué:

  is_admin / is_seller ........ funciones de ayuda para preguntar el rol de un usuario
  IsAdminRole ................. solo administradores
  IsAdminOrReadOnly ........... cualquier usuario con sesión puede leer; solo el admin modifica
  IsSellerOrAdmin ............. lectura pública; escribir requiere ser vendedor o admin
  IsProductOwnerOrAdmin ....... modificar un producto: su vendedor dueño o un admin
  IsMediaOwnerOrAdmin ......... modificar una foto/archivo: el vendedor dueño del producto o un admin

El rol real siempre se decide en el servidor; la app solo oculta botones.
"""
from rest_framework import permissions


def is_admin(user):
    """True si el usuario es administrador (rol ADMIN o staff de Django)."""
    return bool(user and user.is_authenticated and (user.role == 'ADMIN' or user.is_staff))


def is_seller(user):
    return bool(user and user.is_authenticated and user.role == 'SELLER')


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


class IsAdminOrReadOnly(permissions.BasePermission):
    """Lectura para cualquier usuario autenticado; escritura solo para administradores."""

    message = "Solo un administrador puede realizar esta acción."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.method in permissions.SAFE_METHODS or is_admin(request.user)


class IsMediaOwnerOrAdmin(permissions.BasePermission):
    """Medios: lectura pública; escritura de vendedores sobre sus productos y de admins."""

    message = "Solo puedes modificar los archivos de tus propios productos."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        if is_admin(user):
            return True
        return is_seller(user) and obj.product_id is not None and obj.product.seller_id == user.id
