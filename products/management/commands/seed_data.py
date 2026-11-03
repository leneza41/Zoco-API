from django.core.management.base import BaseCommand
from accounts.models import User
from products.models import Product, ProductCategory
from orders.models import Order, OrderItem, OrderStatus
from multimedia.models import Media, MediaType
from notifications.models import Notification, NotificationType
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos iniciales de prueba para Zoco'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Inicializando datos de prueba para Zoco...'))

        # 1. Crear Superusuario / Admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@zoco.local',
                'first_name': 'Admin',
                'last_name': 'Zoco',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            Token.objects.get_or_create(user=admin_user)
            self.stdout.write(self.style.SUCCESS('Superusuario admin creado (admin / admin123)'))

        # 2. Vendedor local
        seller_user, created = User.objects.get_or_create(
            username='vendedor_juan',
            defaults={
                'email': 'juan@panaderiazoco.com',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'role': 'SELLER',
                'phone': '4451234567',
                'address': 'Calle Hidalgo #45, Centro',
                'preferred_language': 'es'
            }
        )
        if created:
            seller_user.set_password('zoco123')
            seller_user.save()
            Token.objects.get_or_create(user=seller_user)
            self.stdout.write(self.style.SUCCESS('Vendedor vendedor_juan creado (vendedor_juan / zoco123)'))

        # 3. Comprador local
        buyer_user, created = User.objects.get_or_create(
            username='laura_compradora',
            defaults={
                'email': 'laura@gmail.com',
                'first_name': 'Laura',
                'last_name': 'Gómez',
                'role': 'BUYER',
                'phone': '4459876543',
                'address': 'Av. Juárez #120, Col. San Miguel',
                'preferred_language': 'es'
            }
        )
        if created:
            buyer_user.set_password('zoco123')
            buyer_user.save()
            Token.objects.get_or_create(user=buyer_user)
            self.stdout.write(self.style.SUCCESS('Comprador laura_compradora creado (laura_compradora / zoco123)'))

        # 4. Catálogo de Productos
        sample_products = [
            {
                'name': 'Pan Rústico de Masa Madre',
                'description': 'Pan recién horneado con fermentación lenta de 24 horas y corteza crujiente.',
                'price': 45.00,
                'category': ProductCategory.BAKERY,
                'producer_name': 'Panadería Tradicional Don Juan',
                'is_express_delivery': True,
                'in_stock': True,
            },
            {
                'name': 'Conchas Artesanales de Vainilla',
                'description': 'Paquete de 4 conchas esponjosas preparadas con mantequilla de rancho y cobertura dulce tradicional.',
                'price': 38.00,
                'category': ProductCategory.BAKERY,
                'producer_name': 'Panadería Tradicional Don Juan',
                'is_express_delivery': True,
                'in_stock': True,
            },
            {
                'name': 'Manzanas Criollas Orgánicas (1 kg)',
                'description': 'Manzanas frescas cosechadas en huerto familiar de la sierra, libres de pesticidas.',
                'price': 32.50,
                'category': ProductCategory.PRODUCE,
                'producer_name': 'Huerto Familiar Los Laureles',
                'is_express_delivery': False,
                'in_stock': True,
            },
            {
                'name': 'Jitomate Saladette de Campo (1 kg)',
                'description': 'Jitomate madurado al sol, ideal para salsas y ensaladas locales.',
                'price': 24.00,
                'category': ProductCategory.PRODUCE,
                'producer_name': 'Hortalizas Don Chente',
                'is_express_delivery': True,
                'in_stock': True,
            },
            {
                'name': 'Queso Oaxaca Artesanal de Rancho (500 g)',
                'description': 'Queso fresco de hebra elaborado con leche bronca 100% natural, ideal para quesadillas.',
                'price': 75.00,
                'category': ProductCategory.DAIRY,
                'producer_name': 'Lácteos del Valle',
                'is_express_delivery': True,
                'in_stock': True,
            },
            {
                'name': 'Yogurt Natural de Búfala / Vaca (1 L)',
                'description': 'Yogurt espeso sin azúcar añadida, fermentación tradicional.',
                'price': 55.00,
                'category': ProductCategory.DAIRY,
                'producer_name': 'Lácteos del Valle',
                'is_express_delivery': False,
                'in_stock': True,
            },
            {
                'name': 'Cesta de Mimbre Tejida a Mano',
                'description': 'Cesta tejida por artesanos de la comunidad con fibras naturales locales.',
                'price': 120.00,
                'category': ProductCategory.CRAFTS,
                'producer_name': 'Artesanías Don Chuy',
                'is_express_delivery': False,
                'in_stock': True,
            },
            {
                'name': 'Taza de Barro Bruñido Esmaltado',
                'description': 'Taza tradicional para café de olla, horneada a baja temperatura con diseño típico.',
                'price': 60.00,
                'category': ProductCategory.CRAFTS,
                'producer_name': 'Alfarería La Esperanza',
                'is_express_delivery': True,
                'in_stock': True,
            },
        ]

        created_products = []
        for pdata in sample_products:
            prod, _ = Product.objects.get_or_create(
                name=pdata['name'],
                defaults={**pdata, 'seller': seller_user}
            )
            created_products.append(prod)
        self.stdout.write(self.style.SUCCESS(f'{len(created_products)} productos creados en catálogo.'))

        # 5. Recursos Multimedia
        if created_products:
            Media.objects.get_or_create(
                product=created_products[0],
                media_type=MediaType.IMAGE,
                defaults={
                    'media_uri': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800',
                    'description': 'Foto del pan rústico recién salido del horno'
                }
            )
            Media.objects.get_or_create(
                product=created_products[4],
                media_type=MediaType.IMAGE,
                defaults={
                    'media_uri': 'https://images.unsplash.com/photo-1559561853-08451507cbe7?w=800',
                    'description': 'Foto del queso oaxaca artesanal'
                }
            )
            self.stdout.write(self.style.SUCCESS('Recursos multimedia de prueba creados.'))

        # 6. Pedido de prueba
        if created_products:
            order, o_created = Order.objects.get_or_create(
                user=buyer_user,
                customer_name='Laura Gómez',
                scheduled_time='Hoy, 16:30 hrs',
                defaults={
                    'customer_phone': '4459876543',
                    'delivery_address': 'Av. Juárez #120, Col. San Miguel',
                    'total_amount': 158.00,
                    'status': OrderStatus.CONFIRMED,
                    'is_express': True,
                    'notes': 'Por favor tocar el timbre blanco al llegar.'
                }
            )
            if o_created:
                OrderItem.objects.create(
                    order=order,
                    product=created_products[0],
                    product_name=created_products[0].name,
                    quantity=2,
                    unit_price=created_products[0].price,
                    subtotal=created_products[0].price * 2
                )
                OrderItem.objects.create(
                    order=order,
                    product=created_products[4],
                    product_name=created_products[4].name,
                    quantity=1,
                    unit_price=created_products[4].price,
                    subtotal=created_products[4].price
                )
                self.stdout.write(self.style.SUCCESS('Pedido de prueba creado con 2 productos.'))

        # 7. Notificaciones de prueba
        Notification.objects.get_or_create(
            user=buyer_user,
            title='¡Bienvenido a Zoco!',
            defaults={
                'message': 'Descubre y apoya a los productores y artesanos de tu comunidad.',
                'type': NotificationType.INFO,
                'is_read': False
            }
        )
        Notification.objects.get_or_create(
            user=buyer_user,
            title='Pedido Confirmado #1',
            defaults={
                'message': 'Tu pedido ha sido recibido y confirmado por Panadería Tradicional Don Juan.',
                'type': NotificationType.ORDER_STATUS,
                'is_read': False
            }
        )
        self.stdout.write(self.style.SUCCESS('Notificaciones de prueba creadas.'))
        self.stdout.write(self.style.SUCCESS('--- Todos los datos iniciales fueron cargados con éxito ---'))
