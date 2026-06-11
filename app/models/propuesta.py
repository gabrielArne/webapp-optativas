from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import EstadoPostulacion, EstadoPropuesta


class Propuesta(Base):
    __tablename__ = "propuestas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    docente_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[str] = mapped_column(String(30), default=EstadoPropuesta.ABIERTA.value, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_last_update: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    docente = relationship("Usuario", back_populates="propuestas")
    postulaciones = relationship("SolicitudPropuesta", back_populates="propuesta", cascade="all, delete-orphan")


class SolicitudPropuesta(Base):
    __tablename__ = "solicitudes_propuesta"
    __table_args__ = (UniqueConstraint("propuesta_id", "alumno_id", name="uq_propuesta_alumno"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    propuesta_id: Mapped[int] = mapped_column(ForeignKey("propuestas.id"), nullable=False)
    alumno_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    estado: Mapped[str] = mapped_column(String(30), default=EstadoPostulacion.PENDIENTE.value, nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_last_update: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    propuesta = relationship("Propuesta", back_populates="postulaciones")
    alumno = relationship("Usuario", back_populates="postulaciones")

