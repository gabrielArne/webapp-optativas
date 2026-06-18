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
            nombre="Emilio",
            apellido="Rasic",
            email="docente1@unsam.edu.ar",
            password_hash=hash_password(TEST_PASSWORD),
            rol=RolUsuario.DOCENTE.value,
        ),
        Usuario(
            nombre="Natalia",
            apellido="Debandi",
            email="docente2@unsam.edu.ar",
            password_hash=hash_password(TEST_PASSWORD),
            rol=RolUsuario.DOCENTE.value,
        ),
        Usuario(
            nombre="Gabriel Santiago",
            apellido="Arnesano",
            email="alumno1@unsam.edu.ar",
            password_hash=hash_password(TEST_PASSWORD),
            rol=RolUsuario.ALUMNO.value,
        ),
        Usuario(
            nombre="Tomas Ramos",
            apellido="Vidal",
            email="alumno2@unsam.edu.ar",
            password_hash=hash_password(TEST_PASSWORD),
            rol=RolUsuario.ALUMNO.value,
        ),
        Usuario(
            nombre="Sol",
            apellido="Crespi",
            email="alumno3@unsam.edu.ar",
            password_hash=hash_password(TEST_PASSWORD),
            rol=RolUsuario.ALUMNO.value,
        ),
        Usuario(
            nombre="Lucas",
            apellido="Oliaro",
            email="alumno4@unsam.edu.ar",
            password_hash=hash_password(TEST_PASSWORD),
            rol=RolUsuario.ALUMNO.value,
        ),
    ]
    db.add_all(users)
    db.flush()

    admin, docente1, docente2, alumno1, alumno2, alumno3, alumno4 = users

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

    project_data = [
        {
            "id": "P13",
            "unit": "EH - CELES / LICH",
            "title": "Lenguas y hablantes en América Latina",
            "desc": "Scraping de medios y agencias estatales para construir un corpus sobre lenguas en la región, con dashboard de mapas.",
        },
        {
            "id": "P18",
            "unit": "EPyG",
            "title": "¿Quién gobierna las provincias argentinas?",
            "desc": "Scraping de LinkedIn, Wikipedia y webs oficiales para actualizar una base de ministros provinciales (2004-2026) y clasificar trayectorias.",
        },
        {
            "id": "P19",
            "unit": "EPyG - IIP",
            "title": "¿Qué es la economía popular? Prensa 2019-2023",
            "desc": "Scraping de La Nación y Página 12 para analizar cómo la prensa construye la idea de economía popular.",
        },
        {
            "id": "P31",
            "unit": "EIDAES - NESDI",
            "title": "Juicio por Jurados de PBA en los medios",
            "desc": "Scraping histórico de portales de noticias (15 años) con modelado de tópicos y análisis temporal.",
        },
        {
            "id": "P03",
            "unit": "EIDAES - PISEX",
            "title": "Anuncios personales en la revista NX (1993-2001)",
            "desc": "~20.000 anuncios ya digitalizados: clasificación y análisis exploratorio con NLP.",
        },
        {
            "id": "P04",
            "unit": "EIDAES",
            "title": "Masculinidades y discursos de odio en Twitter/X",
            "desc": "Corpus de tweets de cuentas libertarias: minería de texto y análisis del discurso, con tablero de monitoreo.",
        },
        {
            "id": "P11",
            "unit": "EEyN - CENIT",
            "title": "Clasificación textual en publicaciones científicas",
            "desc": "Catálogo OpenAlex vía API: clasificación textual y bibliometría para mapear agendas de investigación en IA.",
        },
        {
            "id": "P17",
            "unit": "ECyT - IEU",
            "title": "Representaciones de la ciencia y sesgos algorítmicos",
            "desc": "Producciones estudiantiles + datos de YouTube (API): análisis de contenido y NLP.",
        },
        {
            "id": "P20",
            "unit": "EPyG",
            "title": "Dispositivos médicos y medio ambiente",
            "desc": "Corpus de literatura académica (2000-2026): extracción de texto, bibliometría y NLP.",
        },
        {
            "id": "P35",
            "unit": "EPyG - IIP",
            "title": "El giro en la política comercial argentina entre crisis, 1929-1939",
            "desc": "Corpus de debates parlamentarios argentinos (1929-1939): extracción de texto desde PDF, NER, modelado de tópicos y análisis de sentimiento.",
        },
        {
            "id": "P05",
            "unit": "EIDAES",
            "title": "Simulación de encuestas con LLMs (silicon sampling)",
            "desc": "Simular respuestas de encuesta (World Values Survey) con LLMs y evaluar estadísticamente sus sesgos.",
        },
        {
            "id": "P24",
            "unit": "EPyG",
            "title": "Mapeo causal de riesgos de la IA abierta",
            "desc": "Extracción de relaciones causales con LLMs para comparar beneficios y riesgos de modelos abiertos vs. cerrados.",
        },
        {
            "id": "P26",
            "unit": "ECyT - CIAI / EIDAES",
            "title": "Seguridad, evaluación y gobernanza de la IA",
            "desc": "Mapeo del campo de AI Safety + evaluación empírica de LLMs (sesgos, jailbreaks, calibración).",
        },
        {
            "id": "P12",
            "unit": "EEyN - CENIT / Bioleft",
            "title": "Bioleft: ensayos agronómicos participativos",
            "desc": "ETL y modelo relacional de 5 temporadas + dashboard por variedad/zona y prototipo de bot.",
        },
        {
            "id": "P21",
            "unit": "EPyG - IIP",
            "title": "Respuesta estatal ante protestas (Jujuy/Chubut)",
            "desc": "Integración de fuentes y dashboard interactivo comparativo entre casos subnacionales.",
        },
        {
            "id": "P34",
            "unit": "EIDAES",
            "title": "Financiamiento multilateral de transición energética",
            "desc": "Base de proyectos de IFIs (2014-2022): armonización de datos y dashboards comparativos.",
        },
        {
            "id": "P01",
            "unit": "EByN - INTECH",
            "title": "Interacciones sRNA-mRNA y diseño de bactericidas",
            "desc": "Base de ~32K interacciones: análisis exploratorio y detección de patrones moleculares.",
        },
        {
            "id": "P02",
            "unit": "EEyN - CENIT",
            "title": "Predicción de la pobreza con microdatos de la EPH",
            "desc": "ML supervisado (con SHAP/LIME) sobre microdatos del INDEC.",
        },
        {
            "id": "P22",
            "unit": "EHyS - Inst. de Arquitectura",
            "title": "Materialoteca inteligente para la construcción",
            "desc": "~200 fichas de materiales: ML de clasificación e interfaz inteligente de consulta.",
        },
        {
            "id": "P25",
            "unit": "EByN - IIBio",
            "title": "IA para propiedades estructurales de proteínas",
            "desc": ">20.000 regiones flexibles (AlphaFold): embeddings y modelos supervisados de clasificación.",
        },
        {
            "id": "P28",
            "unit": "EByN - IIBio",
            "title": "Del dato experimental al modelo predictivo",
            "desc": "ML supervisado con embeddings de secuencias sobre interacciones proteína-proteína.",
        },
        {
            "id": "P33",
            "unit": "ECyT - ITECA",
            "title": "IA aplicada al diseño de inmunoterapias",
            "desc": "Integración de datos de secuencias anticuerpo-antígeno y ML inicial.",
        },
        {
            "id": "P08",
            "unit": "ECyT - ICIFI",
            "title": "ML sobre redes dinámicas de proteínas",
            "desc": "Trayectorias de dinámica molecular (GPCRmd): ML y análisis de redes para inferir estados funcionales.",
        },
        {
            "id": "P23",
            "unit": "EAyP - CEPyA",
            "title": "Series ambientales de reservas de museos",
            "desc": "Series de humedad y temperatura: análisis de series temporales y detección de anomalías.",
        },
        {
            "id": "P30",
            "unit": "EAyP - CEPyA / EH",
            "title": "Espectroscopía p-XRF en arte rupestre del NOA",
            "desc": "Espectros de fluorescencia: análisis multivariable y clustering de pigmentos.",
        },
        {
            "id": "P06",
            "unit": "EIDAES",
            "title": "Electorado de derecha radical (estudio diacrónico)",
            "desc": "Audios y textos de grupos de WhatsApp: speech-to-text + NLP y visualizaciones dinámicas.",
        },
        {
            "id": "P14",
            "unit": "EAyP - Centro Espigas",
            "title": "Patrimonio audiovisual: Fondo Arte Canal",
            "desc": "799 cassettes UMATIC digitalizados: extracción automática de metadatos de video y descripción con IA.",
        },
        {
            "id": "P16",
            "unit": "EAyP - CIAP",
            "title": "Cartografías del textil argentino (1915-1935)",
            "desc": "BD histórica: IA multimodal (texto+imagen), análisis geográfico y de redes.",
        },
        {
            "id": "P27",
            "unit": "EPyG",
            "title": "La política memetizada (trumpismo-mileísmo)",
            "desc": "Corpus de memes: computer vision y NLP multimodal para analizar su circulación.",
        },
        {
            "id": "P07",
            "unit": "ECyT",
            "title": "MovEat - App de alimentación y hábitos",
            "desc": "NLP/CNN sobre texto, audio e imagen y un motor de recomendación.",
        },
        {
            "id": "P32",
            "unit": "EIDAES",
            "title": "Infraestructura conversacional agroecológica",
            "desc": "Prototipo de chatbot (LLM) + visualización territorial sobre AgroEco.Red.",
        },
    ]
    docentes_proyectos = [docente1, docente2]
    propuestas = [
        Propuesta(
            docente_id=docentes_proyectos[index % len(docentes_proyectos)].id,
            titulo=project["title"],
            descripcion=f"{project['id']} - {project['unit']}\n{project['desc']}",
        )
        for index, project in enumerate(project_data)
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
