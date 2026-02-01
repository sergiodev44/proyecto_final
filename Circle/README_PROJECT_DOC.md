# Normas para la elaboración del Proyecto Integrado — InnerCircle

1. Definición del proyecto

- Ámbito: InnerCircle es una aplicación para intercambiar y vender ropa entre amigos. En la situación actual de mercado, la gestión de trueques entre redes cercanas carece de una plataforma sencilla que garantice confianza y seguimiento. Esta app facilita encontrar prendas dentro de la red de amigos, gestionar solicitudes de intercambio/compra y comunicarse de forma segura.
- Alcance: Versión 1.0 implementa autenticación, gestión de perfiles, feed de items de amigos, creación/edición/borrado de items, búsqueda de amigos, solicitudes de intercambio/compra y visualización de solicitudes y notificaciones básicas. Funcionalidades avanzadas (leaderboard, gamificación completa, pagos) quedan fuera del alcance inicial.

2. Análisis y requisitos del sistema

a) Modelado de datos

i. BDD Relacionales: Entidades principales: User, Profile, Item, FriendRequest, SwapRequest, Notification.

- Entidad `User` (ya provista por Django auth)
- `Profile` (user_id PK, avatar, bio)
- `Item` (id PK, owner_id FK User, title, description, photo, category, size, created_at)
- `FriendRequest` (id, from_user_id FK User, to_user_id FK User, message, accepted, created_at)
- `SwapRequest` (id, sender_id FK User, receiver_id FK User, item_id FK Item, message, confirmed)
- `Notification` (id, user_id FK User, text, read, created_at)

Normalización: Las tablas anteriores siguen 3FN — cada atributo atómico pertenece a su entidad, claves primarias definidas, sin dependencias transitivas.

ii. BDD No Relacionales: (Opcional) Se podrían usar documentos para almacenar historiales de chat o logs de actividad; por ahora no implementado.

b) MockUp y diagrama de pantallas

- Pantallas principales: Login, Registro, Feed (item_list), Item create/edit, Perfil, Buscar amigos, Solicitudes, Requests list, Notificaciones (futuro).
- Mockups iniciales: usar plantillas Bootstrap incluidas en el repositorio (carpeta `innercircle/templates/innercircle`).

3. Diagrama de Casos de uso

- Autenticación: Registrar, Login, Logout
- Perfil: Ver, Editar
- Items: Crear, Ver, Editar, Borrar, Listar (feed)
- Amigos: Buscar, Enviar solicitud, Aceptar/Rechazar
- Solicitudes: Crear solicitud de swap/compra, Ver solicitudes entrantes/salientes

4. Diagrama de clases

- Clases (modelo): Profile, Item, FriendRequest, SwapRequest, Notification — ver `innercircle/models.py`.

5. Especificación funcional

a. Manual de Usuario

- Registro: Crear cuenta en la pantalla `Register`. Completar usuario, email y contraseña.
- Login: Acceder en `Login`.
- Perfil: Ver tu perfil y los items que has publicado en `Profile`.
- Publicar item: `Post item` en el feed para subir foto y descripción.
- Buscar amigos: `Search Friends` para localizar usuarios y enviar solicitudes.
- Solicitudes: `Requests` para ver solicitudes entrantes y salientes.

b. Manual Técnico

- Tecnología: Django 4.2, PostgreSQL, Bootstrap 5.
- Requisitos: Python 3.10+, PostgreSQL. En desarrollo puede usarse SQLite cambiando `DATABASES` en `config/settings.py`.
- Instalación básica:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- Configurar variables de entorno `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` para PostgreSQL o usar los defaults (recomendado crear DB y usuario en Postgres).
- Ejecutar migraciones y crear superusuario:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

c. Despliegue

- Para producción se recomienda usar Gunicorn/ASGI server + Nginx y servir estáticos desde `collectstatic`.
- HTTPS: emplear un proxy TLS (Let's Encrypt + Nginx) o desplegar en PaaS con HTTPS gestionado (Heroku, Railway, Render).

d. Licencia

- Propuesta: MIT (libre para uso y desarrollo). Añadir `LICENSE` si se confirma.

6. Corolario

a. Análisis crítico / mejoras futuras

- Añadir sistema de confirmación para trueques, historial de transacciones completas, reputación y badges, chat entre usuarios, filtros avanzados y geolocalización.

b. Viabilidad

- Proyecto viable como MVP social-local. Requiere esfuerzos en verificación de usuarios y moderación para escalar.

7. Bibliografía

- Django documentation
- Bootstrap documentation
- Artículos sobre diseño de plataformas peer-to-peer y marketplaces locales

Estilo y maquetación: Documento generado con estructura solicitada; adaptar tipografías y estilo final al entregable (Times New Roman 10.5, interlineado 1.5) en el documento final Word/PDF.
