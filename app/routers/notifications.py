from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import require_user
from app.database.session import get_db
from app.models.notification import Notificacion
from app.models.user import Usuario
from app.utils.templates import page_context, templates

router = APIRouter(prefix="/notificaciones", tags=["notificaciones"])


@router.get("")
def list_notifications(
    request: Request,
    current_user: Usuario = Depends(require_user),
    db: Session = Depends(get_db),
):
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


@router.post("/{notification_id}/leer")
def mark_read(
    notification_id: int,
    current_user: Usuario = Depends(require_user),
    db: Session = Depends(get_db),
):
    notification = db.get(Notificacion, notification_id)
    if notification and notification.usuario_id == current_user.id:
        notification.leida = True
        db.commit()
    return RedirectResponse("/notificaciones", status_code=303)

