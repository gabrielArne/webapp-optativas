import shutil
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import flash, require_roles, require_user
from app.core.config import settings
from app.database.session import get_db
from app.models.banco import BancoMateria
from app.models.enums import EstadoBancoMateria, EstadoSolicitud, RolUsuario, TipoSolicitud
from app.models.solicitud import Adjunto, Feedback, HistorialEstado, Solicitud
from app.models.user import Usuario
from app.services.notifications import notify
from app.utils.templates import page_context, templates

router = APIRouter(prefix="/solicitudes", tags=["solicitudes"])


def can_view(user: Usuario, solicitud: Solicitud) -> bool:
    if user.rol == RolUsuario.ADMIN.value:
        return True
    if user.rol == RolUsuario.DOCENTE.value:
        return solicitud.docente_id in (None, user.id) or solicitud.estado in (
            EstadoSolicitud.ENVIADA.value,
            EstadoSolicitud.EN_REVISION.value,
        )
    return solicitud.alumno_id == user.id


def add_history(db: Session, solicitud: Solicitud, new_state: str, user_id: int) -> None:
    if solicitud.estado == new_state:
        return
    db.add(
        HistorialEstado(
            solicitud_id=solicitud.id,
            estado_anterior=solicitud.estado,
            estado_nuevo=new_state,
            usuario_id=user_id,
        )
    )
    solicitud.estado = new_state
    solicitud.fecha_actualizacion = datetime.utcnow()


def save_uploads(db: Session, solicitud: Solicitud, files: list[UploadFile] | None) -> None:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    for file in files or []:
        if not file.filename:
            continue
        original_name = Path(file.filename).name
        stored_name = f"{uuid4().hex}_{original_name}"
        destination = upload_dir / stored_name
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        db.add(
            Adjunto(
                solicitud_id=solicitud.id,
                nombre_archivo=original_name,
                ruta_archivo=str(destination),
            )
        )


@router.get("")
def list_solicitudes(
    request: Request,
    page: int = 1,
    current_user: Usuario = Depends(require_user),
    db: Session = Depends(get_db),
):
    per_page = 10
    page = max(page, 1)
    query = db.query(Solicitud)
    if current_user.rol == RolUsuario.ALUMNO.value:
        query = query.filter(Solicitud.alumno_id == current_user.id)
    elif current_user.rol == RolUsuario.DOCENTE.value:
        query = query.filter((Solicitud.docente_id == current_user.id) | (Solicitud.docente_id.is_(None)))
    query = query.order_by(Solicitud.fecha_creacion.desc())
    total = query.count()
    solicitudes = query.offset((page - 1) * per_page).limit(per_page).all()
    return templates.TemplateResponse(
        "solicitudes/list.html",
        page_context(
            request,
            current_user=current_user,
            solicitudes=solicitudes,
            page=page,
            total_pages=max((total + per_page - 1) // per_page, 1),
            base_url="/solicitudes",
        ),
    )


@router.get("/nueva")
def new_solicitud_form(
    request: Request,
    current_user: Usuario = Depends(require_roles(RolUsuario.ALUMNO.value)),
    db: Session = Depends(get_db),
):
    docentes = db.query(Usuario).filter(Usuario.rol == RolUsuario.DOCENTE.value, Usuario.activo.is_(True)).all()
    materias_banco = (
        db.query(BancoMateria)
        .filter(BancoMateria.estado == EstadoBancoMateria.APROBADA.value)
        .order_by(BancoMateria.nombre)
        .all()
    )
    return templates.TemplateResponse(
        "solicitudes/form.html",
        page_context(
            request,
            current_user=current_user,
            docentes=docentes,
            materias_banco=materias_banco,
            tipos=[tipo.value for tipo in TipoSolicitud],
        ),
    )


@router.post("")
def create_solicitud(
    request: Request,
    tipo: str = Form(TipoSolicitud.MATERIA.value),
    titulo: str = Form(""),
    descripcion: str = Form(""),
    docente_id: str = Form(""),
    banco_materia_id: str = Form(""),
    files: list[UploadFile] | None = File(None),
    current_user: Usuario = Depends(require_roles(RolUsuario.ALUMNO.value)),
    db: Session = Depends(get_db),
):
    materia_banco = None
    if banco_materia_id:
        try:
            materia_banco = db.get(BancoMateria, int(banco_materia_id))
        except ValueError:
            materia_banco = None
        if not materia_banco or materia_banco.estado != EstadoBancoMateria.APROBADA.value:
            flash(request, "La materia seleccionada no esta disponible.", "danger")
            return RedirectResponse("/solicitudes/nueva", status_code=303)

    if materia_banco:
        docente_id_value = materia_banco.docente_id
        titulo_limpio = materia_banco.nombre
        descripcion_limpia = (
            f"Solicitud de materia del banco.\n"
            f"Carrera: {materia_banco.carrera}\n"
            f"Universidad: {materia_banco.universidad}\n\n"
            f"{materia_banco.descripcion}"
        )
        tipo_value = TipoSolicitud.MATERIA.value
        estado_value = EstadoSolicitud.APROBADA.value
    else:
        docente_id_value = int(docente_id) if docente_id else None
        titulo_limpio = titulo.strip()
        descripcion_limpia = descripcion.strip()
        tipo_value = tipo
        estado_value = EstadoSolicitud.ENVIADA.value
        if not titulo_limpio or not descripcion_limpia:
            flash(request, "Titulo y descripcion son obligatorios.", "danger")
            return RedirectResponse("/solicitudes/nueva", status_code=303)

    solicitud = Solicitud(
        alumno_id=current_user.id,
        docente_id=docente_id_value,
        banco_materia_id=materia_banco.id if materia_banco else None,
        tipo=tipo_value,
        titulo=titulo_limpio,
        descripcion=descripcion_limpia,
        estado=estado_value,
    )
    db.add(solicitud)
    db.flush()
    db.add(
        HistorialEstado(
            solicitud_id=solicitud.id,
            estado_anterior=None,
            estado_nuevo=solicitud.estado,
            usuario_id=current_user.id,
        )
    )
    save_uploads(db, solicitud, files)
    if materia_banco:
        notify(
            db,
            docente_id_value,
            f"Solicitud aprobada automaticamente para la materia del banco: {materia_banco.nombre}",
        )
    else:
        notify(db, docente_id_value, f"Nueva solicitud de {current_user.nombre} {current_user.apellido}: {titulo_limpio}")
    db.commit()
    flash(request, "Solicitud aprobada automaticamente." if materia_banco else "Solicitud enviada.")
    return RedirectResponse(f"/solicitudes/{solicitud.id}", status_code=303)


@router.get("/{solicitud_id}")
def solicitud_detail(
    request: Request,
    solicitud_id: int,
    current_user: Usuario = Depends(require_user),
    db: Session = Depends(get_db),
):
    solicitud = db.get(Solicitud, solicitud_id)
    if not solicitud or not can_view(current_user, solicitud):
        flash(request, "No tenes acceso a esa solicitud.", "danger")
        return RedirectResponse("/solicitudes", status_code=303)
    return templates.TemplateResponse(
        "solicitudes/detail.html",
        page_context(
            request,
            current_user=current_user,
            solicitud=solicitud,
            estados=[estado.value for estado in EstadoSolicitud],
        ),
    )


@router.post("/{solicitud_id}/feedback")
def add_feedback(
    request: Request,
    solicitud_id: int,
    comentario: str = Form(...),
    current_user: Usuario = Depends(require_user),
    db: Session = Depends(get_db),
):
    solicitud = db.get(Solicitud, solicitud_id)
    if not solicitud or not can_view(current_user, solicitud):
        flash(request, "No tenes acceso a esa solicitud.", "danger")
        return RedirectResponse("/solicitudes", status_code=303)
    db.add(Feedback(solicitud_id=solicitud.id, usuario_id=current_user.id, comentario=comentario.strip()))
    if current_user.id == solicitud.alumno_id:
        notify(db, solicitud.docente_id, f"El alumno respondio feedback en: {solicitud.titulo}")
    else:
        notify(db, solicitud.alumno_id, f"Nuevo feedback en tu solicitud: {solicitud.titulo}")
    db.commit()
    flash(request, "Comentario registrado.")
    return RedirectResponse(f"/solicitudes/{solicitud.id}", status_code=303)


@router.post("/{solicitud_id}/estado")
def update_estado(
    request: Request,
    solicitud_id: int,
    estado: str = Form(...),
    comentario: str = Form(""),
    current_user: Usuario = Depends(require_roles(RolUsuario.DOCENTE.value, RolUsuario.ADMIN.value)),
    db: Session = Depends(get_db),
):
    solicitud = db.get(Solicitud, solicitud_id)
    if not solicitud or not can_view(current_user, solicitud):
        flash(request, "No tenes acceso a esa solicitud.", "danger")
        return RedirectResponse("/solicitudes", status_code=303)
    if current_user.rol == RolUsuario.DOCENTE.value and solicitud.docente_id is None:
        solicitud.docente_id = current_user.id
    add_history(db, solicitud, estado, current_user.id)
    if comentario.strip():
        db.add(Feedback(solicitud_id=solicitud.id, usuario_id=current_user.id, comentario=comentario.strip()))
    notify(db, solicitud.alumno_id, f"Tu solicitud '{solicitud.titulo}' cambio a {estado}.")
    db.commit()
    flash(request, "Estado actualizado.")
    return RedirectResponse(f"/solicitudes/{solicitud.id}", status_code=303)


@router.post("/{solicitud_id}/anular")
def cancel_solicitud(
    request: Request,
    solicitud_id: int,
    current_user: Usuario = Depends(require_roles(RolUsuario.ALUMNO.value)),
    db: Session = Depends(get_db),
):
    solicitud = db.get(Solicitud, solicitud_id)
    if not solicitud or solicitud.alumno_id != current_user.id:
        flash(request, "No tenes acceso a esa solicitud.", "danger")
        return RedirectResponse("/solicitudes", status_code=303)
    add_history(db, solicitud, EstadoSolicitud.ANULADA.value, current_user.id)
    notify(db, solicitud.docente_id, f"Solicitud anulada por el alumno: {solicitud.titulo}")
    db.commit()
    flash(request, "Solicitud anulada.")
    return RedirectResponse(f"/solicitudes/{solicitud.id}", status_code=303)


@router.get("/adjuntos/{adjunto_id}/descargar")
def download_adjunto(
    request: Request,
    adjunto_id: int,
    current_user: Usuario = Depends(require_user),
    db: Session = Depends(get_db),
):
    adjunto = db.get(Adjunto, adjunto_id)
    if not adjunto or not can_view(current_user, adjunto.solicitud):
        flash(request, "No tenes acceso al adjunto.", "danger")
        return RedirectResponse("/solicitudes", status_code=303)
    return FileResponse(adjunto.ruta_archivo, filename=adjunto.nombre_archivo)
