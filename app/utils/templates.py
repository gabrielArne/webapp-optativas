from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.auth.dependencies import pop_flash
from app.database.session import SessionLocal
from app.models.notification import Notificacion


templates = Jinja2Templates(directory="app/templates")


def page_context(request: Request, **kwargs):
    current_user = kwargs.get("current_user")
    has_notifications = False
    if current_user:
        with SessionLocal() as db:
            has_notifications = (
                db.query(Notificacion.id).filter(Notificacion.usuario_id == current_user.id).first() is not None
            )

    context = {"request": request, "flash": pop_flash(request), "has_notifications": has_notifications, **kwargs}
    return context
