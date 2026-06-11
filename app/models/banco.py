from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import EstadoBancoMateria


class BancoMateria(Base):
    __tablename__ = "banco_materias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[str] = mapped_column(String(30), default=EstadoBancoMateria.PENDIENTE.value, nullable=False)
    docente_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_last_update: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    docente = relationship("Usuario", back_populates="materias_banco")

