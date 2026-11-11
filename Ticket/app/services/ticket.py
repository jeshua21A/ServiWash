
"""
Servicio encargado de generar tickets y registrar
sus respectivos detalles en la base de datos.
"""

from decimal import Decimal, InvalidOperation

from app.database import get_db_session
from app.models import Ticket, DetalleServicio
from app.services.servicios import cotizar_servicio


def generar_ticket(data):

    try:
        # 1. Obtener datos generales del ticket
        cliente_id = data.get('clientes_id')
        usuario_id = data.get('usuarios_id')
        metodo_pago = data.get('metodo_pago', 'EFECTIVO')

        monto_recibido = Decimal(
            str(data.get('monto_recibido'))
        )

        servicios = data.get('servicios', [])

        # 2. Validar datos obligatorios
        if not cliente_id or not usuario_id:
            raise ValueError(
                "Los identificadores del cliente y usuario son obligatorios"
            )

        if metodo_pago != 'EFECTIVO':
            raise ValueError("Método de pago no permitido")

        if not servicios:
            raise ValueError(
                "El ticket debe contener al menos un servicio"
            )

        if monto_recibido < 0:
            raise ValueError(
                "El monto recibido no puede ser negativo"
            )

        # 3. Solicitar cotización de cada servicio
        detalles = []
        cobro_total = Decimal('0.00')

        for item in servicios:

            servicio_id = item.get('servicios_id')
            metrica = item.get('metrica_cobro')
            datos_cotizacion = item.get('datos')

            if not servicio_id or not metrica or not isinstance(datos_cotizacion, dict):
                raise ValueError(
                    "Cada servicio debe incluir servicios_id, "
                    "metrica_cobro y datos"
                )

            # Consumir el microservicio de servicios
            resultado = cotizar_servicio(
                metrica,
                {
                    **datos_cotizacion,
                    "servicio_id": servicio_id
                }
            )

            # Obtener subtotal
            subtotal = Decimal(
                str(resultado['subtotal_calculado'])
            ).quantize(Decimal('0.01'))

            # Obtener cantidad procesada según la métrica
            if metrica.upper() == 'KILO':
                cantidad = Decimal(
                    str(resultado['cantidad_procesada'])
                )

            elif metrica.upper() == 'USO':
                cantidad = Decimal(
                    str(resultado['numero_ciclos'])
                )

            elif metrica.upper() == 'PRENDA_ESPECIAL':
                cantidad = Decimal(
                    str(resultado['cantidad_piezas'])
                )

            else:
                raise ValueError(
                    f"Métrica no reconocida: {metrica}"
                )

            if cantidad <= 0 or subtotal < 0:
                raise ValueError(
                    "La cantidad debe ser positiva y el subtotal no negativo"
                )

            detalles.append({
                'servicios_id': servicio_id,
                'cantidad': cantidad,
                'subtotal': subtotal
            })

            cobro_total += subtotal

        # 4. Calcular el cambio
        cobro_total = cobro_total.quantize(
            Decimal('0.01')
        )

        if monto_recibido < cobro_total:
            raise ValueError(
                "El monto recibido es insuficiente para cubrir el ticket"
            )

        cambio = (monto_recibido - cobro_total).quantize(
            Decimal('0.01')
        )

        # 5. Registrar ticket y detalles en una transacción
        with get_db_session() as session:

            nuevo_ticket = Ticket(
                cobro_total=cobro_total,
                metodo_pago=metodo_pago,
                monto_recibido=monto_recibido,
                cambio_entregado=cambio,
                clientes_id=cliente_id,
                usuarios_id=usuario_id
            )

            session.add(nuevo_ticket)

            # Obtener el ID generado por MySQL
            session.flush()

            # 6. Registrar los detalles del ticket
            for detalle in detalles:

                nuevo_detalle = DetalleServicio(
                    cantidad=detalle['cantidad'],
                    subtotal=detalle['subtotal'],
                    servicios_id=detalle['servicios_id'],
                    tickets_id=nuevo_ticket.id
                )

                session.add(nuevo_detalle)

            # Confirmar todas las operaciones
            session.commit()

            # 7. Preparar respuesta
            respuesta = {
                "mensaje": "Ticket generado correctamente",
                "ticket": {
                    "id": nuevo_ticket.id,
                    "cobro_total": str(cobro_total),
                    "metodo_pago": nuevo_ticket.metodo_pago,
                    "monto_recibido": str(monto_recibido),
                    "cambio_entregado": str(cambio),
                    "clientes_id": cliente_id,
                    "usuarios_id": usuario_id,
                    "detalles": [
                        {
                            "servicios_id": d['servicios_id'],
                            "cantidad": str(d['cantidad']),
                            "subtotal": str(d['subtotal'])
                        }
                        for d in detalles
                    ]
                }
            }

            return respuesta

    except (InvalidOperation, TypeError) as ex:
        raise ValueError(
            f"Datos numéricos inválidos: {str(ex)}"
        )
