from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import flash, require_roles, require_user
from app.database.session import get_db
from app.models.banco import BancoMateria
from app.models.enums import EstadoBancoMateria, RolUsuario
from app.models.user import Usuario
from app.services.notifications import notify
from app.utils.templates import page_context, templates

router = APIRouter(prefix="/banco", tags=["banco"])


@router.get("")
def list_banco(
    request: Request,
    current_user: Usuario = Depends(require_user),
    db: Session = Depends(get_db),
):
    if current_user.rol == RolUsuario.ADMIN.value:
        return RedirectResponse("/usuarios", status_code=303)

    query = db.query(BancoMateria)
    if current_user.rol == RolUsuario.ALUMNO.value:
        query = query.filter(BancoMateria.estado == EstadoBancoMateria.APROBADA.value)
    materias = query.order_by(BancoMateria.nombre).all()
    return templates.TemplateResponse(
        "banco/list.html",
        page_context(
            request,
            current_user=current_user,
            materias=materias,
            estados=[estado.value for estado in EstadoBancoMateria],
        ),
    )


@router.get("/nueva")
def new_materia_form(
    request: Request,
    current_user: Usuario = Depends(require_roles(RolUsuario.DOCENTE.value, RolUsuario.ADMIN.value)),
):
    if current_user.rol == RolUsuario.ADMIN.value:
        return RedirectResponse("/usuarios", status_code=303)

    return templates.TemplateResponse(
        "banco/form.html",
        page_context(
            request,
            current_user=current_user,
            estados=[estado.value for estado in EstadoBancoMateria],
        ),
    )


@router.post("")
def create_materia(
    request: Request,
    nombre: str = Form(...),
    descripcion: str = Form(...),
    carrera: str = Form(...),
    universidad: str = Form(...),
    estado: str = Form(...),
    current_user: Usuario = Depends(require_roles(RolUsuario.DOCENTE.value, RolUsuario.ADMIN.value)),
    db: Session = Depends(get_db),
):
    nombre_limpio = nombre.strip()
    descripcion_limpia = descripcion.strip()
    carrera_limpia = carrera.strip()
    universidad_limpia = universidad.strip()
    if not nombre_limpio or not descripcion_limpia or not carrera_limpia or not universidad_limpia:
        flash(request, "Nombre, descripcion, carrera y universidad son obligatorios.", "danger")
        return RedirectResponse("/banco/nueva", status_code=303)
    estados_validos = {estado_banco.value for estado_banco in EstadoBancoMateria}
    if estado not in estados_validos:
        flash(request, "El estado seleccionado no es valido.", "danger")
        return RedirectResponse("/banco/nueva", status_code=303)

    db.add(
        BancoMateria(
            nombre=nombre_limpio,
            descripcion=descripcion_limpia,
            carrera=carrera_limpia,
            universidad=universidad_limpia,
            estado=estado,
            docente_id=current_user.id,
        )
    )
    db.commit()
    flash(request, "Materia cargada en el banco.")
    return RedirectResponse("/banco", status_code=303)


@router.post("/{materia_id}/estado")
def update_materia_estado(
    request: Request,
    materia_id: int,
    estado: str = Form(...),
    current_user: Usuario = Depends(require_roles(RolUsuario.DOCENTE.value, RolUsuario.ADMIN.value)),
    db: Session = Depends(get_db),
):
    estados_validos = {estado_banco.value for estado_banco in EstadoBancoMateria}
    if estado not in estados_validos:
        flash(request, "El estado seleccionado no es valido.", "danger")
        return RedirectResponse("/banco", status_code=303)

    materia = db.get(BancoMateria, materia_id)
    if not materia:
        flash(request, "Materia inexistente.", "danger")
        return RedirectResponse("/banco", status_code=303)
    materia.estado = estado
    notify(db, materia.docente_id, f"La materia '{materia.nombre}' cambio a {estado}.")
    db.commit()
    flash(request, "Estado de materia actualizado.")
    return RedirectResponse("/banco", status_code=303)
