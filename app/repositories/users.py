from sqlalchemy.orm import Session

from app.models.user import Usuario


def get_user_by_email(db: Session, email: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.email == email.lower().strip()).first()


def get_user(db: Session, user_id: int) -> Usuario | None:
    return db.get(Usuario, user_id)

