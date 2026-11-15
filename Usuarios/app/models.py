import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum
from app.database import Base

class RolEnum(str, enum.Enum):
    ADMIN = 'ADMIN'
    EMPLEADO = 'EMPLEADO'

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_usuario = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(100), nullable=False)
    rol = Column(Enum(RolEnum), nullable=False)
    esta_activo = Column(Boolean, default=True, nullable=False)

    def to_dict(self):
        # No se incluye password_hash por seguridad
        return {
            "id": self.id,
            "nombre_usuario": self.nombre_usuario,
            "rol": self.rol.value if isinstance(self.rol, enum.Enum) else self.rol,
            "esta_activo": self.esta_activo
        }
