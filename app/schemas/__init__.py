from datetime import datetime

from pydantic import BaseModel, EmailStr


class UsuarioBase(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    rol: str
    activo: bool = True


class UsuarioRead(UsuarioBase):
    id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class SolicitudBase(BaseModel):
    tipo: str
    titulo: str
    descripcion: str


class SolicitudRead(SolicitudBase):
    id: int
    alumno_id: int
    docente_id: int | None
    estado: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True

