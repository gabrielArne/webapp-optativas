from enum import StrEnum


class RolUsuario(StrEnum):
    ADMIN = "Administrador"
    DOCENTE = "Docente"
    ALUMNO = "Alumno"


class TipoSolicitud(StrEnum):
    MATERIA = "Materia"
    PROYECTO = "Proyecto"


class EstadoSolicitud(StrEnum):
    ENVIADA = "ENVIADA"
    EN_REVISION = "EN REVISION"
    REQUIERE_CAMBIOS = "REQUIERE CAMBIOS"
    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"
    CERRADA = "CERRADA"
    ANULADA = "ANULADA"


class EstadoPropuesta(StrEnum):
    ABIERTA = "ABIERTA"
    FINALIZADA = "FINALIZADA"
    CERRADA = "CERRADA"


class EstadoPostulacion(StrEnum):
    PENDIENTE = "PENDIENTE"
    ACEPTADA = "ACEPTADA"
    RECHAZADA = "RECHAZADA"


class EstadoBancoMateria(StrEnum):
    PENDIENTE = "PENDIENTE"
    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"
    INACTIVA = "INACTIVA"

