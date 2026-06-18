from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import EstadoSolicitud, TipoSolicitud


class Solicitud(Base):
    __tablename__ = "solicitudes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alumno_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    docente_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    banco_materia_id: Mapped[int | None] = mapped_column(ForeignKey("banco_materias.id"), nullable=True)
    tipo: Mapped[str] = mapped_column(String(30), default=TipoSolicitud.MATERIA.value, nullable=False)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[str] = mapped_column(String(40), default=EstadoSolicitud.ENVIADA.value, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_last_update: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    alumno = relationship("Usuario", foreign_keys=[alumno_id], back_populates="solicitudes_alumno")
    docente = relationship("Usuario", foreign_keys=[docente_id], back_populates="solicitudes_docente")
    materia_banco = relationship("BancoMateria")
    feedbacks = relationship("Feedback", back_populates="solicitud", cascade="all, delete-orphan")
    adjuntos = relationship("Adjunto", back_populates="solicitud", cascade="all, delete-orphan")
    historial = relationship("HistorialEstado", back_populates="solicitud", cascade="all, delete-orphan")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    solicitud_id: Mapped[int] = mapped_column(ForeignKey("solicitudes.id"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    comentario: Mapped[str] = mapped_column(Text, nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_last_update: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    solicitud = relationship("Solicitud", back_populates="feedbacks")
    usuario = relationship("Usuario", back_populates="feedbacks")


class Adjunto(Base):
    __tablename__ = "adjuntos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    solicitud_id: Mapped[int] = mapped_column(ForeignKey("solicitudes.id"), nullable=False)
    nombre_archivo: Mapped[str] = mapped_column(String(255), nullable=False)
    ruta_archivo: Mapped[str] = mapped_column(String(500), nullable=False)
    fecha_subida: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_last_update: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    solicitud = relationship("Solicitud", back_populates="adjuntos")


class HistorialEstado(Base):
    __tablename__ = "historial_estados"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    solicitud_id: Mapped[int] = mapped_column(ForeignKey("solicitudes.id"), nullable=False)
    estado_anterior: Mapped[str | None] = mapped_column(String(40), nullable=True)
    estado_nuevo: Mapped[str] = mapped_column(String(40), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_last_update: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    solicitud = relationship("Solicitud", back_populates="historial")
    usuario = relationship("Usuario")
