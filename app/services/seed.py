from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.banco import BancoMateria
from app.models.enums import EstadoBancoMateria, EstadoSolicitud, RolUsuario, TipoSolicitud
from app.models.propuesta import Propuesta
from app.models.solicitud import HistorialEstado, Solicitud
from app.models.user import Usuario
from app.services.notifications import notify


TEST_PASSWORD = "admin1234"


def seed_initial_data(db: Session) -> None:
    if db.query(Usuario).first():
        return

    users = [
        Usuario(
            nombre="Admin",
            apellido="UNSAM",
            email="admin@unsam.edu.ar",
            password_hash=hash_password(TEST_PASSWORD),
            rol=RolUsuario.ADMIN.value,
        ),
        Usuario(
            nombre="Docente",
            apellido="Uno",
            email="docente1@unsam.edu.ar",
            password_hash=hash_password(TEST_PASSWORD),
            rol=RolUsuario.DOCENTE.value,
        ),
        Usuario(
            nombre="Docente",
            apellido="Dos",
            email="docente2@unsam.edu.ar",
            password_hash=hash_password(TEST_PASSWORD),
            rol=RolUsuario.DOCENTE.value,
        ),
        Usuario(
            nombre="Alumno",
            apellido="Uno",
            email="alumno1@unsam.edu.ar",
            password_hash=hash_password(TEST_PASSWORD),
            rol=RolUsuario.ALUMNO.value,
        ),
        Usuario(
            nombre="Alumno",
            apellido="Dos",
            email="alumno2@unsam.edu.ar",
            password_hash=hash_password(TEST_PASSWORD),
            rol=RolUsuario.ALUMNO.value,
        ),
        Usuario(
            nombre="Alumno",
            apellido="Tres",
            email="alumno3@unsam.edu.ar",
            password_hash=hash_password(TEST_PASSWORD),
            rol=RolUsuario.ALUMNO.value,
        ),
    ]
    db.add_all(users)
    db.flush()

    admin, docente1, docente2, alumno1, alumno2, alumno3 = users

    materias = [
        BancoMateria(
            nombre="Aprendizaje Automatico Aplicado",
            descripcion="Modelos supervisados y no supervisados con casos reales.",
            carrera="Licenciatura en Ciencia de Datos",
            universidad="UNSAM",
            estado=EstadoBancoMateria.APROBADA.value,
            docente_id=docente1.id,
        ),
        BancoMateria(
            nombre="Procesamiento de Lenguaje Natural",
            descripcion="Tecnicas modernas para texto, embeddings y clasificacion.",
            carrera="Licenciatura en Ciencia de Datos",
            universidad="UNSAM",
            estado=EstadoBancoMateria.APROBADA.value,
            docente_id=docente2.id,
        ),
        BancoMateria(
            nombre="Visualizacion de Datos",
            descripcion="Principios de visualizacion, dashboards y comunicacion.",
            carrera="Licenciatura en Ciencia de Datos",
            universidad="UNSAM",
            estado=EstadoBancoMateria.APROBADA.value,
            docente_id=docente1.id,
        ),
        BancoMateria(
            nombre="Bases de Datos Avanzadas",
            descripcion="Optimizacion, modelado y motores analiticos.",
            carrera="Licenciatura en Ciencia de Datos",
            universidad="UNSAM",
            estado=EstadoBancoMateria.PENDIENTE.value,
            docente_id=docente2.id,
        ),
        BancoMateria(
            nombre="Etica y Gobernanza de Datos",
            descripcion="Privacidad, sesgos, auditoria y gobernanza institucional.",
            carrera="Licenciatura en Ciencia de Datos",
            universidad="UNSAM",
            estado=EstadoBancoMateria.APROBADA.value,
            docente_id=docente1.id,
        ),
    ]
    db.add_all(materias)

    propuestas = [
        Propuesta(
            docente_id=docente1.id,
            titulo="Analisis de trayectorias academicas",
            descripcion="Proyecto para detectar patrones de cursada y permanencia estudiantil.",
        ),
        Propuesta(
            docente_id=docente2.id,
            titulo="Clasificador de consultas administrativas",
            descripcion="Prototipo NLP para categorizar consultas frecuentes.",
        ),
        Propuesta(
            docente_id=docente1.id,
            titulo="Tablero de indicadores para materias optativas",
            descripcion="Construccion de un dashboard con metricas academicas.",
        ),
    ]
    db.add_all(propuestas)

    solicitudes = [
        Solicitud(
            alumno_id=alumno1.id,
            docente_id=docente1.id,
            tipo=TipoSolicitud.MATERIA.value,
            titulo="Reconocimiento de Aprendizaje Automatico Aplicado",
            descripcion="Solicito cursar la materia como optativa de la licenciatura.",
            estado=EstadoSolicitud.ENVIADA.value,
        ),
        Solicitud(
            alumno_id=alumno2.id,
            docente_id=docente2.id,
            tipo=TipoSolicitud.PROYECTO.value,
            titulo="Proyecto NLP para consultas UNSAM",
            descripcion="Interes en desarrollar un clasificador de consultas.",
            estado=EstadoSolicitud.EN_REVISION.value,
        ),
        Solicitud(
            alumno_id=alumno3.id,
            docente_id=docente1.id,
            tipo=TipoSolicitud.MATERIA.value,
            titulo="Visualizacion de Datos como optativa",
            descripcion="Presento programa y fundamentos para la solicitud.",
            estado=EstadoSolicitud.REQUIERE_CAMBIOS.value,
        ),
    ]
    db.add_all(solicitudes)
    db.flush()

    for solicitud in solicitudes:
        db.add(
            HistorialEstado(
                solicitud_id=solicitud.id,
                estado_anterior=None,
                estado_nuevo=solicitud.estado,
                usuario_id=admin.id,
            )
        )
        notify(db, solicitud.alumno_id, f"Solicitud creada: {solicitud.titulo}")

    db.commit()
