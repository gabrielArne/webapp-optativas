# Optativas UNSAM

MVP monolitico para gestionar solicitudes de materias optativas y proyectos de la Licenciatura en Ciencia de Datos de la Universidad Nacional de San Martin.

## Stack

- Python 3.12+
- FastAPI
- SQLAlchemy ORM
- SQLite por defecto, PostgreSQL configurable
- Jinja2 + Bootstrap
- Autenticacion por sesion y passwords hasheadas con bcrypt/passlib

## Instalacion

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.main
```

La aplicacion queda disponible en:

```text
http://127.0.0.1:8000
```

## Configuracion

La base de datos se configura solo con `DATABASE_URL`.

SQLite local:

```env
DATABASE_URL=sqlite:///./app.db
```

PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg2://usuario:password@host:5432/base
```

No usa Alembic. En este MVP las tablas se crean automaticamente con `Base.metadata.create_all(bind=engine)` al iniciar la app.

## Usuarios iniciales

Todos usan la password:

```text
admin1234
```

Administrador:

- `admin@unsam.edu.ar`

Docentes:

- `docente1@unsam.edu.ar`
- `docente2@unsam.edu.ar`

Alumnos:

- `alumno1@unsam.edu.ar`
- `alumno2@unsam.edu.ar`
- `alumno3@unsam.edu.ar`

Tambien se cargan automaticamente 5 materias del banco, 3 propuestas y 3 solicitudes de ejemplo.

## Funcionalidades incluidas

- Login, logout y registro de alumnos.
- RBAC para Administrador, Docente y Alumno.
- Gestion de usuarios desde Administrador.
- Creacion, consulta, anulacion y evaluacion de solicitudes.
- Cambio de estados con historial.
- Feedback docente-alumno y carga de avances como comentarios.
- Subida y descarga de adjuntos.
- Banco de materias con aprobacion/rechazo/cambio de estado.
- Propuestas docentes y postulaciones de alumnos.
- Aceptacion/rechazo de alumnos en propuestas.
- Notificaciones internas.

## Estructura

```text
app/
  main.py
  core/
  database/
  models/
  schemas/
  routers/
  services/
  repositories/
  auth/
  templates/
  static/
  notifications/
  uploads/
  utils/
```

