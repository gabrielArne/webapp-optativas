from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import Usuario
from app.repositories.users import get_user


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> Usuario | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    user = get_user(db, int(user_id))
    if not user or not user.activo:
        request.session.clear()
        return None
    return user


def require_user(
    current_user: Usuario | None = Depends(get_current_user),
) -> Usuario:
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"},
            detail="Debe iniciar sesion.",
        )
    return current_user


def require_roles(*roles: str) -> Callable:
    def dependency(current_user: Usuario = Depends(require_user)) -> Usuario:
        if current_user.rol not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso no autorizado.")
        return current_user

    return dependency


def flash(request: Request, message: str, category: str = "success") -> None:
    request.session["flash"] = {"message": message, "category": category}


def pop_flash(request: Request) -> dict | None:
    return request.session.pop("flash", None)

