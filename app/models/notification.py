from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    leida: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_last_update: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    usuario = relationship("Usuario", back_populates="notificaciones")

