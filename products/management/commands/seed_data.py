from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from accounts.models import User
from products.models import Product, ProductCategory
from orders.models import Order, OrderItem, OrderStatus
from multimedia.models import Media, MediaType
from notifications.models import Notification, NotificationType
from rest_framework.authtoken.models import Token

# Fotos de ejemplo (créditos en docs/CREDITOS_FOTOS.md de la app)
SEED_PHOTOS_DIR = Path(__file__).resolve().parent / 'seed_photos'


class Command(BaseCommand):
    help = 'Pobla la base de datos con productos (con foto), pedidos y usuarios de ejemplo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Elimina productos y pedidos previos antes de poblar',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Cargando catálogo, pedidos y fotos de ejemplo...'))

        # Limpiar pedidos, productos, notificaciones y multimedia para no duplicar
        Order.objects.all().delete()
        Product.objects.all().delete()
        Notification.objects.all().delete()
        Media.objects.all().delete()

        # 1. Crear Superusuario / Admin
        admin_user, _ = User.objects.get_or_create(
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
        admin_user.set_password('admin123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        Token.objects.get_or_create(user=admin_user)
        self.stdout.write(self.style.SUCCESS('Superusuario admin configurado (admin / admin123)'))

        # 2. Vendedor local verificado en la API
        seller_user, _ = User.objects.get_or_create(
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
        seller_user.set_password('zoco123')
        seller_user.save()
        Token.objects.get_or_create(user=seller_user)

        # 3. Comprador registrado
        buyer_user, _ = User.objects.get_or_create(
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
        buyer_user.set_password('zoco123')
        buyer_user.save()
        Token.objects.get_or_create(user=buyer_user)

        # 3b. Segundo vendedor (Artesana María)
        maria_user, _ = User.objects.get_or_create(
            username='artesana_maria',
            defaults={
                'email': 'maria@artesaniazoco.com',
                'first_name': 'María',
                'last_name': 'López',
                'role': 'SELLER',
                'phone': '4452223344',
                'address': 'Calle Allende #18, Barrio Artesanal',
                'preferred_language': 'es'
            }
        )
        maria_user.set_password('zoco123')
        maria_user.role = 'SELLER'
        maria_user.save()
        Token.objects.get_or_create(user=maria_user)

        # 4. Catálogo de Productos ONLINE (Sin emojis)
        sample_products = [
            {
                'photo': 'sample_pan.jpg',
                'name': 'Pan Rústico de Masa Madre',
                'description': 'Fermentación lenta de 24 horas y corteza dorada.',
                'price': 45.00,
                'category': ProductCategory.BAKERY,
                'producer_name': 'Panadería Don Juan',
                'is_express_delivery': True,
                'in_stock': True,
            },
            {
                'photo': 'sample_conchas.jpg',
                'name': 'Conchas Artesanales de Vainilla',
                'description': 'Paquete con 4 conchas esponjosas elaboradas con mantequilla de rancho y vainilla natural.',
                'price': 38.00,
                'category': ProductCategory.BAKERY,
                'producer_name': 'Panadería Don Juan',
                'is_express_delivery': True,
                'in_stock': True,
            },
            {
                'photo': 'sample_cafe.jpg',
                'name': 'Café Gourmet de Altura (500g)',
                'description': 'Grano arábica tostado medio cultivado a más de 1,200 msnm. Empacado con válvula desgasificadora.',
                'price': 135.00,
                'category': ProductCategory.PRODUCE,
                'producer_name': 'Cooperativa Café Sierra',
                'is_express_delivery': True,
                'in_stock': True,
            },
            {
                'photo': 'sample_manzanas.jpg',
                'name': 'Manzanas Criollas Orgánicas (1 kg)',
                'description': 'Manzanas frescas cosechadas en huerto familiar de montaña, libres de pesticidas químicos.',
                'price': 32.50,
                'category': ProductCategory.PRODUCE,
                'producer_name': 'Huerto Los Laureles',
                'is_express_delivery': False,
                'in_stock': True,
            },
            {
                'photo': 'sample_jitomate.jpg',
                'name': 'Jitomate Saladette de Campo (1 kg)',
                'description': 'Madurado en planta al sol con riego de pozo profundo. Textura firme y alto rendimiento.',
                'price': 24.00,
                'category': ProductCategory.PRODUCE,
                'producer_name': 'Hortalizas Don Chente',
                'is_express_delivery': True,
                'in_stock': True,
            },
            {
                'photo': 'sample_queso.jpg',
                'name': 'Queso Oaxaca Artesanal de Rancho (500g)',
                'description': 'Queso fresco de hebra 100% leche bronca entera, con el tradicional punto de sal y fundido perfecto.',
                'price': 75.00,
                'category': ProductCategory.DAIRY,
                'producer_name': 'Lácteos del Valle',
                'is_express_delivery': True,
                'in_stock': True,
            },
            {
                'photo': 'sample_yogurt.jpg',
                'name': 'Yogurt Natural de Búfala / Vaca (1 L)',
                'description': 'Cremoso, espeso y sin conservadores ni azúcares añadidos.',
                'price': 55.00,
                'category': ProductCategory.DAIRY,
                'producer_name': 'Lácteos del Valle',
                'is_express_delivery': False,
                'in_stock': True,
            },
            {
                'photo': 'sample_canasta.jpg',
                'name': 'Cesta de Mimbre Tejida a Mano',
                'description': 'Fibras naturales tratadas a mano por maestros artesanos locales para compras sustentables.',
                'price': 120.00,
                'category': ProductCategory.CRAFTS,
                'producer_name': 'Artesanías Don Chuy',
                'is_express_delivery': False,
                'in_stock': True,
            },
            {
                'photo': 'sample_taza.jpg',
                'name': 'Taza de Barro Bruñido Esmaltado',
                'description': 'Taza artesanal libre de plomo para bebidas calientes con sello térmico tradicional.',
                'price': 60.00,
                'category': ProductCategory.CRAFTS,
                'producer_name': 'Alfarería La Esperanza',
                'is_express_delivery': True,
                'in_stock': True,
            },
            {
                'photo': 'sample_chocolate.jpg',
                'name': 'Chocolate de Mesa Tradicional (400g)',
                'description': 'Tablillas artesanales con cacao criollo tostado en comal de barro y canela de Ceilán.',
                'price': 85.00,
                'category': ProductCategory.BAKERY,
                'producer_name': 'Chocolatería Oaxaca',
                'is_express_delivery': True,
                'in_stock': True,
            },
        ]

        created_products = []
        for idx, pdata in enumerate(sample_products):
            owner = seller_user if idx < 6 else maria_user
            photo = pdata.pop('photo')
            prod = Product.objects.create(**pdata, seller=owner)
            with open(SEED_PHOTOS_DIR / photo, 'rb') as f:
                prod.image.save(photo, ContentFile(f.read()), save=True)
            created_products.append(prod)

        self.stdout.write(self.style.SUCCESS(f'{len(created_products)} productos creados en el catálogo.'))

        # 5. Pedidos Web API (Sin emojis, identificados como [En Línea])
        orders_data = [
            {
                'customer_name': 'Laura Gómez',
                'customer_phone': '4459876543',
                'delivery_address': 'Av. Juárez #120, Col. San Miguel',
                'scheduled_time': 'Hoy, 16:30 hrs',
                'total_amount': 158.00,
                'status': OrderStatus.CONFIRMED,
                'is_express': True,
                'notes': 'Pedido confirmado por el vendedor.',
                'items': [
                    {'product': created_products[0], 'qty': 2, 'price': 45.00},
                    {'product': created_products[5], 'qty': 1, 'price': 68.00},
                ]
            },
            {
                'customer_name': 'Carlos Méndez',
                'customer_phone': '4451122334',
                'delivery_address': 'Calle Zaragoza #45, Zona Centro',
                'scheduled_time': 'Hoy, 18:00 hrs',
                'total_amount': 220.00,
                'status': OrderStatus.DELIVERED,
                'is_express': True,
                'notes': 'Entregado a domicilio por repartidor local.',
                'items': [
                    {'product': created_products[2], 'qty': 1, 'price': 135.00},
                    {'product': created_products[9], 'qty': 1, 'price': 85.00},
                ]
            },
            {
                'customer_name': 'Roberto Gordillo',
                'customer_phone': '4453344556',
                'delivery_address': 'Prolongación Hidalgo #300, Col. Campestre',
                'scheduled_time': 'Mañana, 10:00 hrs',
                'total_amount': 100.00,
                'status': OrderStatus.PREPARING,
                'is_express': True,
                'notes': 'En cocina preparando el horneado de conchas.',
                'items': [
                    {'product': created_products[1], 'qty': 2, 'price': 38.00},
                    {'product': created_products[4], 'qty': 1, 'price': 24.00},
                ]
            },
            {
                'customer_name': 'Ricardo Pérez',
                'customer_phone': '4457788990',
                'delivery_address': 'Calzada del Tepeyac #88, Col. Bellavista',
                'scheduled_time': 'Mañana, 12:30 hrs',
                'total_amount': 180.00,
                'status': OrderStatus.OUT_FOR_DELIVERY,
                'is_express': False,
                'notes': 'Repartidor en ruta para entrega comunitaria.',
                'items': [
                    {'product': created_products[7], 'qty': 1, 'price': 120.00},
                    {'product': created_products[8], 'qty': 1, 'price': 60.00},
                ]
            },
            {
                'customer_name': 'Leonardo Nuñez',
                'customer_phone': '4455566778',
                'delivery_address': 'Fraccionamiento Las Palmas #12',
                'scheduled_time': 'Hoy, 19:15 hrs',
                'total_amount': 130.00,
                'status': OrderStatus.PENDING,
                'is_express': True,
                'notes': 'Pedido recién recibido.',
                'items': [
                    {'product': created_products[5], 'qty': 1, 'price': 75.00},
                    {'product': created_products[6], 'qty': 1, 'price': 55.00},
                ]
            },
        ]

        for o_info in orders_data:
            items_list = o_info.pop('items')
            order = Order.objects.create(user=buyer_user, **o_info)
            for item in items_list:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    product_name=item['product'].name,
                    quantity=item['qty'],
                    unit_price=item['price'],
                    subtotal=item['price'] * item['qty']
                )

        self.stdout.write(self.style.SUCCESS(f'{len(orders_data)} pedidos de ejemplo creados.'))

        # 6. Notificaciones Web API (Sin emojis)
        Notification.objects.create(
            user=buyer_user,
            title='Catálogo Sincronizado',
            message='El catálogo se actualizó con productos de tu comunidad.',
            type=NotificationType.INFO,
            is_read=False
        )
        Notification.objects.create(
            user=buyer_user,
            title='Pedido Confirmado #1',
            message='Tu pedido #1 fue confirmado.',
            type=NotificationType.ORDER_STATUS,
            is_read=False
        )

        self.stdout.write(self.style.SUCCESS('--- Datos de ejemplo cargados ---'))
