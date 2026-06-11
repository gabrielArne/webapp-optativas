from sqlalchemy.orm import Session

from app.models.notification import Notificacion


def notify(db: Session, usuario_id: int | None, mensaje: str) -> None:
    if usuario_id is None:
        return
    db.add(Notificacion(usuario_id=usuario_id, mensaje=mensaje))

