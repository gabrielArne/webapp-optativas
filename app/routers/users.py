from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import flash, require_roles
from app.core.security import hash_password
from app.database.session import get_db
from app.models.enums import RolUsuario
from app.models.user import Usuario
from app.repositories.users import get_user_by_email
from app.utils.templates import page_context, templates

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("")
def list_users(
    request: Request,
    page: int = 1,
    current_user: Usuario = Depends(require_roles(RolUsuario.ADMIN.value)),
    db: Session = Depends(get_db),
):
    per_page = 10
    page = max(page, 1)
    query = db.query(Usuario).order_by(Usuario.rol, Usuario.apellido, Usuario.nombre)
    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()
    return templates.TemplateResponse(
        "users/list.html",
        page_context(
            request,
            current_user=current_user,
            users=users,
            roles=[role.value for role in RolUsuario],
            page=page,
            total_pages=max((total + per_page - 1) // per_page, 1),
            base_url="/usuarios",
        ),
    )


@router.post("")
def create_user(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    rol: str = Form(...),
    current_user: Usuario = Depends(require_roles(RolUsuario.ADMIN.value)),
    db: Session = Depends(get_db),
):
    if get_user_by_email(db, email):
        flash(request, "Ya existe un usuario con ese email.", "danger")
        return RedirectResponse("/usuarios", status_code=303)
    db.add(
        Usuario(
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            email=email.lower().strip(),
            password_hash=hash_password(password),
            rol=rol,
            activo=True,
        )
    )
    db.commit()
    flash(request, "Usuario creado.")
    return RedirectResponse("/usuarios", status_code=303)


@router.post("/{user_id}/actualizar")
def update_user(
    request: Request,
    user_id: int,
    nombre: str = Form(...),
    apellido: str = Form(...),
    rol: str = Form(...),
    activo: bool = Form(False),
    current_user: Usuario = Depends(require_roles(RolUsuario.ADMIN.value)),
    db: Session = Depends(get_db),
):
    user = db.get(Usuario, user_id)
    if user:
        user.nombre = nombre.strip()
        user.apellido = apellido.strip()
        user.rol = rol
        user.activo = activo
        db.commit()
        flash(request, "Usuario actualizado.")
    return RedirectResponse("/usuarios", status_code=303)
