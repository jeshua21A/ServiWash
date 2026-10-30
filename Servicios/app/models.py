import enum
from sqlalchemy import Column, Integer, Numeric, Boolean, Enum
from app.database import Base

class TipoServicioEnum(str, enum.Enum):
    SERVICIO_POR_KILO = 'SERVICIO_POR_KILO' 
    SERVICIO_POR_USO = 'SERVICIO_POR_USO'
    SERVICIO_ESPECIAL = 'SERVICIO_POR_PRENDA_ESPECIAL' 

class MetricaCobroEnum(str, enum.Enum):
    PAGO_POR_KILO = 'PAGO_POR_KILO' 
    PAGO_POR_USO = 'PAGO_POR_USO'
    PAGO_ESPECIAL = 'PAGO_POR_PRENDA_ESPECIAL'

class Servicio(Base):
    __tablename__ = 'servicios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo_servicio = Column(Enum(TipoServicioEnum), nullable=False)
    metrica_cobro = Column(Enum(MetricaCobroEnum), nullable=False)
    costo_referencia = Column(Numeric(10, 2), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "tipo_servicio": self.tipo_servicio.value if isinstance(self.tipo_servicio, enum.Enum) else self.tipo_servicio,
            "metrica_cobro": self.metrica_cobro.value if isinstance(self.metrica_cobro, enum.Enum) else self.metrica_cobro,
            "costo_referencia": float(self.costo_referencia)
        }