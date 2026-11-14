from sqlalchemy import Column, Integer, DECIMAL, TIMESTAMP, Enum, ForeignKey, func
from app.database import Base

class Ticket(Base):
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cobro_total = Column (DECIMAL(10,2), nullable=False) 
    metodo_pago = Column(Enum('EFECTIVO'), nullable=False, default='EFECTIVO')
    monto_recibido = Column(DECIMAL(10,2), nullable=False)
    cambio_entregado = Column(DECIMAL(10,2), nullable=False, default=0.00)
    fecha_registro = Column(TIMESTAMP, nullable=False, default=func.current_timestamp())
    clientes_id = Column(Integer, nullable=False)
    usuarios_id = Column(Integer, nullable=False)

class DetalleServicio(Base):
    __tablename__ = 'detallesservicio'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cantidad = Column(DECIMAL(10, 2), nullable=False, default=1.00)
    subtotal = Column(DECIMAL(10, 2), nullable=False)
    servicios_id = Column(Integer, nullable=False)
    tickets_id = Column(Integer,  ForeignKey('tickets.id'), nullable=False)