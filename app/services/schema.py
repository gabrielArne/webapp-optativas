from sqlalchemy import inspect, text

from app.database.session import engine


def ensure_runtime_schema() -> None:
    """Small schema patcher for MVP deployments without Alembic."""
    with engine.begin() as connection:
        inspector = inspect(connection)
        statements = []
        if inspector.has_table("solicitudes_propuesta"):
            columns = {column["name"] for column in inspector.get_columns("solicitudes_propuesta")}
            if "observacion" not in columns:
                statements.append("ALTER TABLE solicitudes_propuesta ADD COLUMN observacion TEXT NOT NULL DEFAULT ''")
            if "nombre_archivo" not in columns:
                statements.append("ALTER TABLE solicitudes_propuesta ADD COLUMN nombre_archivo VARCHAR(255)")
            if "ruta_archivo" not in columns:
                statements.append("ALTER TABLE solicitudes_propuesta ADD COLUMN ruta_archivo VARCHAR(500)")

        if inspector.has_table("propuestas"):
            columns = {column["name"] for column in inspector.get_columns("propuestas")}
            if "documentacion_nombre_archivo" not in columns:
                statements.append("ALTER TABLE propuestas ADD COLUMN documentacion_nombre_archivo VARCHAR(255)")
            if "documentacion_ruta_archivo" not in columns:
                statements.append("ALTER TABLE propuestas ADD COLUMN documentacion_ruta_archivo VARCHAR(500)")

        for statement in statements:
            connection.execute(text(statement))
