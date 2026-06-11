from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.auth.dependencies import pop_flash


templates = Jinja2Templates(directory="app/templates")


def page_context(request: Request, **kwargs):
    context = {"request": request, "flash": pop_flash(request), **kwargs}
    return context

