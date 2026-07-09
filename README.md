
<div align="center">

# 🍽️ AutoMenu AI
**SaaS de menús digitales para restaurantes, potenciado por IA**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![Stripe](https://img.shields.io/badge/Stripe-635BFF?style=for-the-badge&logo=stripe&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)
![Status](https://img.shields.io/badge/Estado-✅%20Activo-brightgreen?style=for-the-badge)

> *Subí tus platillos, generá contenido con IA, compartí tu menú con un QR.*

</div>

---

## 🖼️ Vista previa

<div align="center">

<!-- 📸 Reemplazá esta URL con una captura real del menú público o del dashboard -->
![Vista previa de AutoMenu AI](./assets/preview.png)

</div>

---

## ✨ Funcionalidades

<table>
<tr>
<td align="center" width="33%">

### 📱 Menú digital + QR
Genera un código QR único por restaurante que enlaza directo al menú público.

</td>
<td align="center" width="33%">

### 🤖 Descripciones con IA
Crea descripciones atractivas de cada platillo a partir del nombre e ingredientes.

</td>
<td align="center" width="33%">

### ✍️ Captions para redes
Genera captions con emojis y hashtags listos para publicar en Instagram/Facebook.

</td>
</tr>
<tr>
<td align="center" width="33%">

### 📷 Escaneo de menú físico
Sube una foto de un menú impreso y la IA de visión extrae los platillos automáticamente.

</td>
<td align="center" width="33%">

### 🌎 Traducción automática
Detecta el idioma del navegador del cliente y traduce el menú público sin que nadie lo pida.

</td>
<td align="center" width="33%">

### 💳 Plan Free / Pro
Plan gratis con hasta 10 platillos; Plan Pro (Stripe, modo test) desbloquea IA ilimitada.

</td>
</tr>
<tr>
<td align="center" width="33%">

### 🖼️ Subida de imágenes
Sube fotos de platillos y del restaurante directo a Supabase Storage.

</td>
<td align="center" width="33%">

### 📊 Dashboard administrativo
Total de platillos, estado del menú, accesos rápidos y estadísticas.

</td>
<td align="center" width="33%">

### 🔐 Autenticación segura
Login y registro con Supabase Auth; sesión manejada por Flask.

</td>
</tr>
</table>

---

## 🧠 ¿Cómo funciona?

```
┌─────────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐
│      📥 INPUT        │      │     ⚙️ PROCESO        │      │      📤 OUTPUT       │
│                     │      │                     │      │                     │
│  🍔 Datos del platillo│─────▶│  🧠 Prompt creado   │─────▶│  📝 Descripción IA   │
│  📷 Foto del menú    │      │  📡 API OpenAI      │      │  ✍️ Caption / Tags   │
│                     │      │  🔄 Procesando...   │      │  🌎 Traducción       │
└─────────────────────┘      └─────────────────────┘      └─────────────────────┘
```

El dueño del restaurante crea su perfil y sus platillos (a mano o escaneando una foto del menú), **AutoMenu AI** arma el prompt, lo manda a la API de OpenAI, y guarda/muestra el resultado directo en el menú digital.

---

## 🛠️ Stack tecnológico

<div align="center">

| Tecnología | Rol en el proyecto | Badge |
|:---:|:---|:---:|
| **Python / Flask** | Backend y rutas de la aplicación | ![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white) |
| **Supabase** | Base de datos (Postgres), Auth y Storage | ![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white) |
| **OpenAI** | Generación de texto (gpt-4o-mini) y visión (gpt-4o) | ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white) |
| **Stripe** | Suscripción al Plan Pro (modo test/sandbox) | ![Stripe](https://img.shields.io/badge/Stripe-635BFF?style=flat-square&logo=stripe&logoColor=white) |
| **qrcode** | Generación del código QR del menú | ![QR](https://img.shields.io/badge/qrcode-000000?style=flat-square&logo=qr-code&logoColor=white) |
| **Bootstrap 5** | Estilos e interfaz responsive | ![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=flat-square&logo=bootstrap&logoColor=white) |
| **Vercel** | Hosting y deploy continuo desde GitHub | ![Vercel](https://img.shields.io/badge/Vercel-000000?style=flat-square&logo=vercel&logoColor=white) |

</div>

---

## 📁 Estructura del proyecto

```
🍽️ AutoMenu AI/
│
├── 🐍 app.py               # Rutas de Flask (auth, dashboard, dishes, IA, Stripe)
├── 🗄️ db.py                 # Acceso a Supabase (tablas + storage + auth)
├── 🧮 menu_logic.py         # Lógica de negocio pura (validaciones, recursión)
├── 🤖 ai_utils.py           # Funciones que llaman a la API de OpenAI
├── 💳 stripe_utils.py       # Integración de Stripe (checkout, verificación de pago)
├── ⚠️ error_handler.py      # Manejo centralizado de errores
├── 🎨 templates/           # Vistas Jinja2 (HTML)
├── 🎨 static/css/styles.css # Paleta crema/beige + verde sobrio
├── 📋 requirements.txt     # Dependencias del proyecto
├── ⚙️ vercel.json           # Configuración de deploy en Vercel
├── 🙈 .gitignore           # Archivos ignorados por Git
├── 📖 README.md            # Este archivo
└── 🔐 .env                 # Variables de entorno (⚠️ NO se sube a GitHub)
```

> ⚠️ **Importante:** El archivo `.env` contiene claves de Supabase, OpenAI y Stripe. Verificá que esté incluido en `.gitignore` para **no exponerlas públicamente**.

---

## ⚙️ Instalación

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/jose-giron-27/proyecto-final.git
cd proyecto-final
```

### 2️⃣ Instalar dependencias
```bash
python3 -m pip install -r requirements.txt
```

### 3️⃣ Crear el archivo `.env`
En la raíz del proyecto, creá un archivo llamado `.env` con tus claves:
```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_supabase_key_aqui
OPENAI_API_KEY=tu_openai_key_aqui
STRIPE_SECRET_KEY=sk_test_tu_stripe_key_aqui
STRIPE_PRICE_ID_PRO=price_tu_price_id_aqui
FLASK_SECRET_KEY=una_clave_secreta_cualquiera
```

> 💡 Obtené tus claves en [supabase.com](https://supabase.com), [platform.openai.com/api-keys](https://platform.openai.com/api-keys) y [dashboard.stripe.com/test/apikeys](https://dashboard.stripe.com/test/apikeys)

---

## ▶️ Ejecutar la aplicación

Desde la terminal, dentro de la carpeta del proyecto:
```bash
python3 app.py
```

La app también está desplegada en Vercel: **[proyecto-final-nu-puce.vercel.app](https://proyecto-final-nu-puce.vercel.app)**

---

## 📌 Guía de uso

```
① Creás tu cuenta ──▶ ② Configurás tu restaurante ──▶ ③ Agregás platillos
                                                              │
                                          ┌───────────────────┼───────────────────┐
                                          ▼                   ▼                   ▼
                                   🤖 Generás con IA    📱 Generás el QR    🌎 Clientes ven el menú
```

| Paso | Acción |
|:---:|:---|
| 1️⃣ | Registrate e iniciá sesión |
| 2️⃣ | Completá el perfil de tu restaurante (nombre, logo, contacto) |
| 3️⃣ | Agregá platillos a mano **o** escaneá una foto de tu menú físico |
| 4️⃣ | Generá descripciones, captions, etiquetas y combos con IA *(Plan Pro)* |
| 5️⃣ | Descargá tu código QR y compartilo en tus mesas |
| 6️⃣ | Tus clientes escanean el QR y ven el menú traducido a su idioma automáticamente |

---

## ⚠️ Limitaciones conocidas

| ⚡ | Limitación | Detalle |
|:---:|:---:|:---|
| 🔒 | Plan Gratis | Máximo 10 platillos, sin funciones de IA |
| 💳 | Stripe en modo test | Simulación de pago, no se procesan cobros reales |
| 🌐 | Conexión requerida | Necesita internet para Supabase, OpenAI y Stripe |
| 🔑 | Claves válidas | Se requieren API keys activas de Supabase, OpenAI y Stripe |

---

## 🎯 Objetivo del proyecto

<div align="center">

> *"AutoMenu AI nació para que cualquier restaurante pequeño pueda tener un menú digital profesional, sin diseñador ni fotógrafo, en minutos."*

</div>

Combina **gestión de restaurantes**, **inteligencia artificial generativa** y **pagos simulados** en una sola plataforma web.
Desarrollado como **Proyecto Final** del curso de **Fundamentos de Programación** en la **Universidad Francisco Marroquín (UFM)**.

---

## 🚀 Estado del proyecto

<div align="center">

| Feature | Estado |
|:---|:---:|
| 🔐 Autenticación (Supabase Auth) | ✅ |
| 🍔 CRUD de platillos | ✅ |
| 📱 Generación de código QR | ✅ |
| 🤖 Descripciones, captions, tags, combos con IA | ✅ |
| 📷 Escaneo de menú con IA de visión | ✅ |
| 🌎 Traducción automática para turistas | ✅ |
| 💳 Suscripción Plan Pro con Stripe (test) | ✅ |
| 🎨 Paleta de colores e interfaz personalizada | ✅ |
| ☁️ Deploy en Vercel | ✅ |

</div>

---

## 👨‍💻 Autores

<div align="center">

**José Daniel Girón Cabrera** · **Isabella Hernández**
*Fundamentos de Programación · Proyecto Final · UFM*

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/jose-giron-27/proyecto-final)

</div>

---

<div align="center">

*Hecho con 💙 y demasiado café ☕ · AutoMenu AI © 2026*

</div>