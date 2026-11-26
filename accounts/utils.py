from .models import User

DEFAULT_USER_SPECS = (
    {
        'username': 'laura_compradora',
        'password': 'zoco123',
        'defaults': {
            'role': 'BUYER',
            'first_name': 'Laura',
            'last_name': 'Gómez',
            'email': 'laura@gmail.com',
            'phone': '4459876543',
            'address': 'Av. Juárez #120, Col. San Miguel',
            'preferred_language': 'es',
        },
    },
    {
        'username': 'vendedor_juan',
        'password': 'zoco123',
        'defaults': {
            'role': 'SELLER',
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'email': 'juan@panaderiazoco.com',
            'phone': '4451234567',
            'address': 'Calle Hidalgo #45, Centro',
            'preferred_language': 'es',
        },
    },
    {
        'username': 'admin',
        'password': 'admin123',
        'defaults': {
            'role': 'ADMIN',
            'first_name': 'Admin',
            'last_name': 'Zoco',
            'email': 'admin@zoco.local',
            'is_staff': True,
            'is_superuser': True,
        },
    },
)

DEFAULT_USERNAMES = tuple(spec['username'] for spec in DEFAULT_USER_SPECS)


def ensure_default_users():
    """Crea de forma idempotente los 3 usuarios predefinidos si aún no existen."""
    created_users = {}
    for spec in DEFAULT_USER_SPECS:
        user, created = User.objects.get_or_create(
            username=spec['username'],
            defaults=spec['defaults'],
        )
        if created:
            user.set_password(spec['password'])
            user.save()
        created_users[spec['username']] = user
    return created_users
