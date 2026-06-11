from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import RolUsuario


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(30), default=RolUsuario.ALUMNO.value, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_last_update: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    solicitudes_alumno = relationship("Solicitud", foreign_keys="Solicitud.alumno_id", back_populates="alumno")
    solicitudes_docente = relationship("Solicitud", foreign_keys="Solicitud.docente_id", back_populates="docente")
    feedbacks = relationship("Feedback", back_populates="usuario")
    propuestas = relationship("Propuesta", back_populates="docente")
    postulaciones = relationship("SolicitudPropuesta", back_populates="alumno")
    notificaciones = relationship("Notificacion", back_populates="usuario")
    materias_banco = relationship("BancoMateria", back_populates="docente")

