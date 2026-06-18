from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import require_user
from app.database.session import get_db
from app.models.banco import BancoMateria
from app.models.enums import EstadoBancoMateria, EstadoPostulacion, EstadoPropuesta, EstadoSolicitud, RolUsuario
from app.models.propuesta import Propuesta, SolicitudPropuesta
from app.models.solicitud import Solicitud
from app.models.user import Usuario
from app.utils.templates import page_context, templates

router = APIRouter()


@router.get("/")
def dashboard(
    request: Request,
    current_user: Usuario = Depends(require_user),
    db: Session = Depends(get_db),
):
    if current_user.rol == RolUsuario.ADMIN.value:
        return RedirectResponse("/usuarios", status_code=303)

    if current_user.rol == RolUsuario.DOCENTE.value:
        pending = (
            db.query(Solicitud)
            .filter(Solicitud.estado.in_([EstadoSolicitud.ENVIADA.value, EstadoSolicitud.EN_REVISION.value]))
            .order_by(Solicitud.fecha_creacion.desc())
            .all()
        )
        postulaciones_pendientes = (
            db.query(SolicitudPropuesta)
            .join(Propuesta)
            .filter(
                Propuesta.docente_id == current_user.id,
                SolicitudPropuesta.estado == EstadoPostulacion.PENDIENTE.value,
            )
            .order_by(SolicitudPropuesta.fecha.desc())
            .all()
        )
        propuestas = (
            db.query(Propuesta)
            .filter(Propuesta.docente_id == current_user.id)
            .order_by(Propuesta.fecha_creacion.desc())
            .limit(5)
            .all()
        )
        materias = (
            db.query(BancoMateria)
            .filter(BancoMateria.estado == EstadoBancoMateria.APROBADA.value)
            .order_by(BancoMateria.nombre)
            .limit(5)
            .all()
        )
        return templates.TemplateResponse(
            "dashboard/docente.html",
            page_context(
                request,
                current_user=current_user,
                pending=pending,
                postulaciones_pendientes=postulaciones_pendientes,
                propuestas=propuestas,
                materias=materias,
            ),
        )

    solicitudes = (
        db.query(Solicitud)
        .filter(Solicitud.alumno_id == current_user.id)
        .order_by(Solicitud.fecha_creacion.desc())
        .all()
    )
    postulaciones = (
        db.query(SolicitudPropuesta)
        .filter(SolicitudPropuesta.alumno_id == current_user.id)
        .order_by(SolicitudPropuesta.fecha.desc())
        .all()
    )
    propuestas = (
        db.query(Propuesta)
        .filter(Propuesta.estado == EstadoPropuesta.ABIERTA.value)
        .order_by(Propuesta.fecha_creacion.desc())
        .limit(5)
        .all()
    )
    materias = (
        db.query(BancoMateria)
        .filter(BancoMateria.estado == EstadoBancoMateria.APROBADA.value)
        .order_by(BancoMateria.nombre)
        .limit(5)
        .all()
    )
    return templates.TemplateResponse(
        "dashboard/alumno.html",
        page_context(
            request,
            current_user=current_user,
            solicitudes=solicitudes,
            postulaciones=postulaciones,
            propuestas=propuestas,
            materias=materias,
        ),
    )
