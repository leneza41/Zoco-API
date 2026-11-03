# Zoco API - Django REST Framework Backend

Backend y API REST oficial para la plataforma **Zoco** (Comercio Electrónico Hiperlocal para el Emprendimiento Tradicional y Local).

Diseñado y optimizado para integrarse directamente con la aplicación móvil Android desarrollada con Jetpack Compose y Retrofit.

---

## 🚀 Tecnologías y Herramientas

- **Python 3.15+**
- **Django 6.1+** (Framework web y ORM)
- **Django REST Framework (DRF)** (Construcción de API REST serializada en JSON)
- **django-cors-headers** (Soporte CORS para emuladores Android y clientes web)
- **django-filter** (Filtros por categoría, precio, entrega express, búsqueda)
- **Pillow** (Gestión y subida de imágenes y fotos de productos)
- **SQLite3** (Base de datos relacional para desarrollo local)
- **Token & Session Authentication** (Autenticación para compradores y vendedores)

---

## 📂 Arquitectura del Proyecto

```text
Zoco-API/
├── zoco_api/                 # Configuración principal del proyecto
│   ├── settings.py           # Ajustes, apps, CORS, DRF, autenticación
│   ├── urls.py               # Enrutamiento raíz y versionado (/api/v1/ y /api/)
│   ├── wsgi.py
│   └── asgi.py
├── accounts/                 # Gestión de usuarios, perfiles y autenticación
│   ├── models.py             # Modelo User extendido con roles (BUYER, SELLER, ADMIN)
│   ├── serializers.py        # Serializadores de Registro, Login y Perfil
│   ├── views.py              # Endpoints de autenticación y tokens
│   ├── urls.py
│   └── admin.py
├── products/                 # Catálogo de productos locales
│   ├── models.py             # Modelo Product con categorías y flags
│   ├── serializers.py        # Serializador con soporte camelCase / Moshi
│   ├── views.py              # ViewSet completo (CRUD, búsqueda, filtros)
│   ├── filters.py            # Filtros por categoría, express, stock
│   ├── management/commands/  # Comando seed_data para poblar datos de prueba
│   ├── urls.py
│   └── admin.py
├── orders/                   # Gestión de pedidos y carritos de compras
│   ├── models.py             # Modelos Order y OrderItem
│   ├── serializers.py        # Serializador anidado para pedidos y renglones
│   ├── views.py              # ViewSet de pedidos y cambio de estado
│   ├── urls.py
│   └── admin.py
├── multimedia/               # Archivos multimedia y galerías de productos
│   ├── models.py             # Modelo Media (fotos, videos)
│   ├── serializers.py        # Serializador con resolución de URL absoluta
│   ├── views.py
│   └── urls.py
├── notifications/            # Sistema de notificaciones
│   ├── models.py             # Modelo Notification con tipos y leídos
│   ├── serializers.py        # Serializador con timestamp en milisegundos
│   ├── views.py              # ViewSet con acciones mark_read y mark_all_read
│   └── urls.py
├── requirements.txt          # Dependencias del proyecto
├── manage.py                 # CLI de administración de Django
└── README.md
```

---

## 🛠️ Instalación y Puesta en Marcha

### 1. Clonar el repositorio y acceder a la carpeta
```bash
git clone https://github.com/leneza41/Zoco-API.git
cd Zoco-API
```

### 2. Crear y activar entorno virtual
En Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

En Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones de base de datos
```bash
python manage.py migrate
```

### 5. Cargar datos de prueba (Seed Data)
Se incluye un comando personalizado que crea usuarios, catálogo con 8 productos locales en distintas categorías, pedidos y notificaciones:
```bash
python manage.py seed_data
```

#### Credenciales predeterminadas generadas por `seed_data`:
| Rol | Usuario | Contraseña | Propósito |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Acceso a panel Django Admin (`/admin/`) |
| **Vendedor** | `vendedor_juan` | `zoco123` | Don Juan Panadero (Vendedor local) |
| **Comprador** | `laura_compradora` | `zoco123` | Laura Gómez (Cliente local) |

### 6. Ejecutar pruebas unitarias automatizadas
```bash
python manage.py test
```

### 7. Iniciar el servidor de desarrollo
```bash
python manage.py runserver 0.0.0.0:8000
```
El servidor quedará disponible en `http://localhost:8000/` o `http://127.0.0.1:8000/`.

---

## 📡 Endpoints de la API REST

Ruta base recomendada: `/api/v1/` (o directamente `/api/`).

### 📦 1. Productos (`/api/v1/products`)

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/v1/products` | Lista de productos (retorna array JSON directo `[...]` para Retrofit). |
| `GET` | `/api/v1/products/{id}` | Detalle de un producto específico. |
| `POST` | `/api/v1/products` | Dar de alta un nuevo producto (acepta camelCase y snake_case). |
| `PUT` / `PATCH` | `/api/v1/products/{id}` | Actualizar un producto existente. |
| `DELETE` | `/api/v1/products/{id}` | Eliminar un producto. |

#### Filtros y Búsqueda disponibles en `/api/v1/products`:
- **Categoría:** `?category=BAKERY` (`ALL`, `BAKERY`, `PRODUCE`, `DAIRY`, `CRAFTS`)
- **Entrega Express:** `?isExpressDelivery=true`
- **En Stock:** `?inStock=true`
- **Búsqueda por texto:** `?search=pan` (busca en nombre, descripción y productor)
- **Rango de precios:** `?min_price=20&max_price=80`
- **Ordenamiento:** `?ordering=price` o `?ordering=-price` o `?ordering=-created_at`

#### Ejemplo de respuesta JSON de producto (Compatible con Moshi / Kotlin):
```json
{
  "id": 1,
  "name": "Pan Rústico de Masa Madre",
  "description": "Pan recién horneado con fermentación lenta de 24 horas y corteza crujiente.",
  "price": 45.0,
  "category": "BAKERY",
  "producerName": "Panadería Tradicional Don Juan",
  "isExpressDelivery": true,
  "inStock": true,
  "imageUrl": null,
  "created_at": "2026-11-02T19:16:30.123456-06:00",
  "updated_at": "2026-11-02T19:16:30.123456-06:00"
}
```

---

### 🛒 2. Pedidos (`/api/v1/orders`)

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/v1/orders` | Listar pedidos registrados. |
| `POST` | `/api/v1/orders` | Crear un pedido con sus renglones (items) desde el carrito. |
| `GET` | `/api/v1/orders/{id}` | Detalle de pedido con desglose de items y totales. |
| `POST` | `/api/v1/orders/{id}/status/` | Cambiar estado del pedido (`CONFIRMED`, `PREPARING`, `OUT_FOR_DELIVERY`, `DELIVERED`, `CANCELLED`). |

#### Ejemplo de payload `POST /api/v1/orders`:
```json
{
  "customerName": "Laura Gómez",
  "customerPhone": "4459876543",
  "deliveryAddress": "Av. Juárez #120, Col. San Miguel",
  "scheduledTime": "Hoy, 16:30 hrs",
  "isExpress": true,
  "notes": "Tocar el timbre blanco",
  "items": [
    {
      "productId": 1,
      "quantity": 2,
      "unitPrice": 45.0
    },
    {
      "productId": 5,
      "quantity": 1,
      "unitPrice": 75.0
    }
  ]
}
```

---

### 🖼️ 3. Multimedia (`/api/v1/media`)

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/v1/media` | Listar recursos multimedia. |
| `POST` | `/api/v1/media` | Subir archivo de imagen o asociar URL/URI externa a un producto. |
| `GET` | `/api/v1/media/{id}` | Obtener detalle de archivo multimedia. |
| `DELETE` | `/api/v1/media/{id}` | Eliminar multimedia. |

---

### 🔔 4. Notificaciones (`/api/v1/notifications`)

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/v1/notifications` | Listar notificaciones del sistema o usuario. |
| `POST` | `/api/v1/notifications/{id}/read/` | Marcar notificación específica como leída. |
| `POST` | `/api/v1/notifications/mark-all-read/` | Marcar todas las notificaciones como leídas. |

---

### 👤 5. Autenticación y Cuentas (`/api/v1/auth/`)

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register/` | Registro de nuevo usuario (comprador o vendedor) con retorno de Token. |
| `POST` | `/api/v1/auth/login/` | Iniciar sesión con `username` y `password`, retorna Token y datos de usuario. |
| `POST` | `/api/v1/auth/logout/` | Invalidar token de sesión actual. |
| `GET` | `/api/v1/auth/profile/` | Consultar perfil del usuario autenticado. |
| `PUT` / `PATCH` | `/api/v1/auth/profile/` | Actualizar datos del perfil (teléfono, dirección, idioma). |

Para peticiones autenticadas, enviar el header HTTP:
```http
Authorization: Token <tu_token_aqui>
```

---

## 📱 Conexión desde la Aplicación Android (Retrofit)

### 1. Dirección IP según entorno de ejecución:
- **En el Emulador de Android oficial:**  
  La máquina host responde en la IP especial `10.0.2.2`.
  ```kotlin
  // En RetrofitClient.kt
  private const val DEFAULT_BASE_URL = "http://10.0.2.2:8000/api/v1/"
  ```
- **En Dispositivo Físico Android (misma red WiFi):**  
  Usar la IP local de tu PC (ejemplo `http://192.168.1.XX:8000/api/v1/`).

### 2. Permitir tráfico HTTP local en Android:
En `app/src/main/AndroidManifest.xml`:
```xml
<application
    android:usesCleartextTraffic="true"
    ... >
```
O configurar un archivo `res/xml/network_security_config.xml` permitiendo `10.0.2.2` o `localhost`.

---

## 📄 Licencia

Proyecto desarrollado para fines académicos y de impacto social comunitario en comercio tradicional.
