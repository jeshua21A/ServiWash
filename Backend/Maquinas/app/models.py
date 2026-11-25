import enum
from sqlalchemy import Column, Integer, Numeric, Enum
from app.database import Base

class TipoMaquinaEnum(str, enum.Enum):
    LAVADORA = 'LAVADORA'
    SECADORA = 'SECADORA'

class EstadoMaquinaEnum(str, enum.Enum):
    OCUPADA = 'OCUPADA'
    DISPONIBLE = 'DISPONIBLE'
    EN_MANTENIMIENTO = 'EN_MANTENIMIENTO'

class Maquina(Base):
    __tablename__ = 'maquinas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo_maquina = Column(Enum(TipoMaquinaEnum), nullable=False)
    capacidad = Column(Numeric(5, 2), nullable=False)
    tiempo_ciclo = Column(Integer, nullable=False)
    estado = Column(Enum(EstadoMaquinaEnum), default=EstadoMaquinaEnum.DISPONIBLE, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "tipo_maquina": self.tipo_maquina.value if isinstance(self.tipo_maquina, enum.Enum) else self.tipo_maquina,
            "capacidad": float(self.capacidad),
            "tiempo_ciclo": self.tiempo_ciclo,
            "estado": self.estado.value if isinstance(self.estado, enum.Enum) else self.estado
        }
    
