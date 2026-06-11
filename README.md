# Optativas UNSAM

MVP monolitico para gestionar solicitudes de materias optativas y proyectos de la Licenciatura en Ciencia de Datos de la Universidad Nacional de San Martin.

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

