import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import flash, require_roles, require_user
from app.core.config import settings
from app.database.session import get_db
from app.models.enums import EstadoPostulacion, EstadoPropuesta, RolUsuario
from app.models.propuesta import Propuesta, SolicitudPropuesta
from app.models.user import Usuario
from app.services.notifications import notify
from app.utils.templates import page_context, templates

router = APIRouter(prefix="/propuestas", tags=["propuestas"])


def save_propuesta_documentacion(documentacion: UploadFile) -> tuple[str, str]:
    upload_dir = Path(settings.upload_dir) / "propuestas" / "documentacion"
    upload_dir.mkdir(parents=True, exist_ok=True)
    original_name = Path(documentacion.filename or "documentacion").name
    stored_name = f"{uuid4().hex}_{original_name}"
    destination = upload_dir / stored_name
    with destination.open("wb") as buffer:
        shutil.copyfileobj(documentacion.file, buffer)
    return original_name, str(destination)


@router.get("")
def list_propuestas(
    request: Request,
    current_user: Usuario = Depends(require_user),
    db: Session = Depends(get_db),
):
    if current_user.rol == RolUsuario.ADMIN.value:
        return RedirectResponse("/usuarios", status_code=303)

    query = db.query(Propuesta)
    if current_user.rol == RolUsuario.ALUMNO.value:
        query = query.filter(Propuesta.estado == EstadoPropuesta.ABIERTA.value)
    elif current_user.rol == RolUsuario.DOCENTE.value:
        query = query.filter(Propuesta.docente_id == current_user.id)
    propuestas = query.order_by(Propuesta.fecha_creacion.desc()).all()
    return templates.TemplateResponse(
        "propuestas/list.html",
        page_context(request, current_user=current_user, propuestas=propuestas),
    )


@router.get("/nueva")
def new_propuesta_form(
    request: Request,
    current_user: Usuario = Depends(require_roles(RolUsuario.DOCENTE.value, RolUsuario.ADMIN.value)),
):
    if current_user.rol == RolUsuario.ADMIN.value:
        return RedirectResponse("/usuarios", status_code=303)

    return templates.TemplateResponse("propuestas/form.html", page_context(request, current_user=current_user))


@router.post("")
def create_propuesta(
    request: Request,
    titulo: str = Form(...),
    descripcion: str = Form(...),
    documentacion: UploadFile | None = File(None),
    current_user: Usuario = Depends(require_roles(RolUsuario.DOCENTE.value, RolUsuario.ADMIN.value)),
    db: Session = Depends(get_db),
):
    propuesta = Propuesta(docente_id=current_user.id, titulo=titulo.strip(), descripcion=descripcion.strip())
    if documentacion and documentacion.filename:
        nombre_archivo, ruta_archivo = save_propuesta_documentacion(documentacion)
        propuesta.documentacion_nombre_archivo = nombre_archivo
        propuesta.documentacion_ruta_archivo = ruta_archivo

    db.add(propuesta)
    db.commit()
    flash(request, "Propuesta creada.")
    return RedirectResponse("/propuestas", status_code=303)


@router.get("/{propuesta_id}")
def propuesta_detail(
    request: Request,
    propuesta_id: int,
    current_user: Usuario = Depends(require_user),
    db: Session = Depends(get_db),
):
    if current_user.rol == RolUsuario.ADMIN.value:
        return RedirectResponse("/usuarios", status_code=303)

    propuesta = db.get(Propuesta, propuesta_id)
    if not propuesta:
        flash(request, "Propuesta inexistente.", "danger")
        return RedirectResponse("/propuestas", status_code=303)
    return templates.TemplateResponse(
        "propuestas/detail.html",
        page_context(
            request,
            current_user=current_user,
            propuesta=propuesta,
            estados_postulacion=[estado.value for estado in EstadoPostulacion],
        ),
    )


@router.get("/{propuesta_id}/documentacion")
def download_propuesta_documentacion(
    request: Request,
    propuesta_id: int,
    current_user: Usuario = Depends(require_user),
    db: Session = Depends(get_db),
):
    propuesta = db.get(Propuesta, propuesta_id)
    if not propuesta or not propuesta.documentacion_ruta_archivo:
        flash(request, "La propuesta no tiene documentacion complementaria.", "danger")
        return RedirectResponse("/propuestas", status_code=303)

    file_path = Path(propuesta.documentacion_ruta_archivo)
    if not file_path.exists():
        flash(request, "No se encontro el archivo de la propuesta.", "danger")
        return RedirectResponse(f"/propuestas/{propuesta.id}", status_code=303)

    return FileResponse(file_path, filename=propuesta.documentacion_nombre_archivo)


@router.post("/{propuesta_id}/postular")
def apply_propuesta(
    request: Request,
    propuesta_id: int,
    observacion: str = Form(...),
    documentacion: UploadFile | None = File(None),
    current_user: Usuario = Depends(require_roles(RolUsuario.ALUMNO.value)),
    db: Session = Depends(get_db),
):
    propuesta = db.get(Propuesta, propuesta_id)
    if not propuesta or propuesta.estado != EstadoPropuesta.ABIERTA.value:
        flash(request, "La propuesta no esta disponible.", "danger")
        return RedirectResponse("/propuestas", status_code=303)
    observacion_limpia = observacion.strip()
    if not observacion_limpia:
        flash(request, "La observacion es obligatoria para postularse.", "danger")
        return RedirectResponse(f"/propuestas/{propuesta.id}", status_code=303)

    postulacion = SolicitudPropuesta(
        propuesta_id=propuesta.id,
        alumno_id=current_user.id,
        observacion=observacion_limpia,
    )
    if documentacion and documentacion.filename:
        upload_dir = Path(settings.upload_dir) / "propuestas"
        upload_dir.mkdir(parents=True, exist_ok=True)
        original_name = Path(documentacion.filename).name
        stored_name = f"{uuid4().hex}_{original_name}"
        destination = upload_dir / stored_name
        with destination.open("wb") as buffer:
            shutil.copyfileobj(documentacion.file, buffer)
        postulacion.nombre_archivo = original_name
        postulacion.ruta_archivo = str(destination)

    db.add(postulacion)
    try:
        notify(db, propuesta.docente_id, f"Nuevo alumno postulado a la propuesta: {propuesta.titulo}")
        db.commit()
        flash(request, "Postulacion enviada.")
    except IntegrityError:
        db.rollback()
        flash(request, "Ya te postulaste a esa propuesta.", "warning")
    return RedirectResponse(f"/propuestas/{propuesta.id}", status_code=303)


@router.get("/postulaciones/{postulacion_id}/adjunto")
def download_postulacion_adjunto(
    request: Request,
    postulacion_id: int,
    current_user: Usuario = Depends(require_user),
    db: Session = Depends(get_db),
):
    postulacion = db.get(SolicitudPropuesta, postulacion_id)
    if not postulacion or not postulacion.ruta_archivo:
        flash(request, "La postulacion no tiene documentacion adjunta.", "danger")
        return RedirectResponse("/propuestas", status_code=303)
    puede_descargar = (
        current_user.rol == RolUsuario.ADMIN.value
        or postulacion.alumno_id == current_user.id
        or (current_user.rol == RolUsuario.DOCENTE.value and postulacion.propuesta.docente_id == current_user.id)
    )
    if not puede_descargar:
        flash(request, "No tenes acceso a ese adjunto.", "danger")
        return RedirectResponse("/propuestas", status_code=303)
    return FileResponse(postulacion.ruta_archivo, filename=postulacion.nombre_archivo)


@router.post("/postulaciones/{postulacion_id}/estado")
def update_postulacion(
    request: Request,
    postulacion_id: int,
    estado: str = Form(...),
    current_user: Usuario = Depends(require_roles(RolUsuario.DOCENTE.value, RolUsuario.ADMIN.value)),
    db: Session = Depends(get_db),
):
    postulacion = db.get(SolicitudPropuesta, postulacion_id)
    if not postulacion or (
        current_user.rol == RolUsuario.DOCENTE.value and postulacion.propuesta.docente_id != current_user.id
    ):
        flash(request, "No tenes acceso a esa postulacion.", "danger")
        return RedirectResponse("/propuestas", status_code=303)
    postulacion.estado = estado
    notify(db, postulacion.alumno_id, f"Tu postulacion a '{postulacion.propuesta.titulo}' cambio a {estado}.")
    db.commit()
    flash(request, "Postulacion actualizada.")
    return RedirectResponse(f"/propuestas/{postulacion.propuesta_id}", status_code=303)


@router.post("/{propuesta_id}/finalizar")
def finish_propuesta(
    request: Request,
    propuesta_id: int,
    current_user: Usuario = Depends(require_roles(RolUsuario.DOCENTE.value, RolUsuario.ADMIN.value)),
    db: Session = Depends(get_db),
):
    propuesta = db.get(Propuesta, propuesta_id)
    if not propuesta or (current_user.rol == RolUsuario.DOCENTE.value and propuesta.docente_id != current_user.id):
        flash(request, "No tenes acceso a esa propuesta.", "danger")
        return RedirectResponse("/propuestas", status_code=303)
    propuesta.estado = EstadoPropuesta.FINALIZADA.value
    db.commit()
    flash(request, "Propuesta finalizada.")
    return RedirectResponse(f"/propuestas/{propuesta.id}", status_code=303)
