from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import flash
from app.core.security import hash_password, verify_password
from app.database.session import get_db
from app.models.enums import RolUsuario
from app.models.user import Usuario
from app.repositories.users import get_user_by_email
from app.utils.templates import page_context, templates

router = APIRouter()


@router.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse("auth/login.html", page_context(request))


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_user_by_email(db, email)
    if not user or not user.activo or not verify_password(password, user.password_hash):
        flash(request, "Credenciales invalidas o usuario inactivo.", "danger")
        return RedirectResponse("/login", status_code=303)

    request.session["user_id"] = user.id
    flash(request, f"Bienvenido/a, {user.nombre}.")
    return RedirectResponse("/", status_code=303)


@router.get("/registro")
def register_form(request: Request):
    return templates.TemplateResponse("auth/register.html", page_context(request))


@router.post("/registro")
def register(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    if get_user_by_email(db, email):
        flash(request, "Ya existe un usuario con ese email.", "danger")
        return RedirectResponse("/registro", status_code=303)

    user = Usuario(
        nombre=nombre.strip(),
        apellido=apellido.strip(),
        email=email.lower().strip(),
        password_hash=hash_password(password),
        rol=RolUsuario.ALUMNO.value,
    )
    db.add(user)
    db.commit()
    flash(request, "Registro creado. Ya podes iniciar sesion.")
    return RedirectResponse("/login", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)

