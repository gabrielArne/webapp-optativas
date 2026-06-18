from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import require_user
from app.database.session import get_db
from app.models.notification import Notificacion
from app.models.enums import RolUsuario
from app.models.user import Usuario
from app.utils.templates import page_context, templates

router = APIRouter(prefix="/notificaciones", tags=["notificaciones"])


@router.get("")
def list_notifications(
    request: Request,
    current_user: Usuario = Depends(require_user),
    db: Session = Depends(get_db),
):
    if current_user.rol == RolUsuario.ADMIN.value:
        return RedirectResponse("/usuarios", status_code=303)

    notifications = (
        db.query(Notificacion)
        .filter(Notificacion.usuario_id == current_user.id)
        .order_by(Notificacion.fecha.desc())
        .all()
    )
    return templates.TemplateResponse(
        "notifications.html",
        page_context(request, current_user=current_user, notifications=notifications),
    )
