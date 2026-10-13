import logging
from database import Client, get_session
from sqlalchemy import select, update, delete

#logger de repositorio
logger = logging.getLogger(__file__)

#repositorio de cliente
class ClientRepository:
    #operaciones
    def get_clients(self, page:int = 0, per_page:int = 10)->list:
        #contenedores
        clients = []
        
        #obtener la sesion
        with get_session() as session:
            #obtener todos los clientes guardados
            stmt = select(Client).limit(per_page).offset(per_page*page)
            
            #ejecutar la query
            result = session.execute(stmt)
            
            #mapear cliente
            client = None
            for row in result.all():
                #obtener clientes
                client = row.tuple()[0]
                client = client.__dict__.copy()
                client.pop('_sa_instance_state')
                
                #añadir diccionario
                clients.append(client)
               
        return clients
    
    def get_client(self, id:int)->dict|None:
        #contenedor
        client = None
        
        #manejo de error
        try:
            #obtener la sesion
            with get_session() as session:
                #preparar sentencia
                stmt = select(Client).where(Client.id == id)
                
                #ejecutar sentencia
                res = session.execute(stmt)
                
                #obtener cliente
                client = res.first().tuple()[0]
                
                #validar resultado
                if not client:
                    raise Exception(f"client {id} not found")
                
                client = client.__dict__.copy()
                client.pop('_sa_instance_state')
        except Exception as e:
            #log de error
            logger.error(e)
            
        return client
    
    def create_client(self,data:dict)->int|None:
        #contenedor
        id = None
        
        #manejo de error
        try:
            #obtener la sesion
            with get_session() as session:
                #preparar la sentencia
                cli = Client(**data)
                
                #ejecutar la sentencia
                session.add(cli)
                session.commit()
                
                #obtener el id insertado
                id = cli.id
        except Exception as e:
            #log de error
            logger.error(e)
        
        #retornar el id
        return id
    
    def update_client(self, id:int, data:dict)->bool:
        #manejo de error
        try:
            #obtener la sesion
            with get_session() as session:
                #preparar la sentencia
                stmt = update(Client).where(Client.id == id).values(**data)
                
                #ejecutar sentencia
                session.execute(stmt)
                
                #guardar cambios
                session.commit()
            
            #retornar exito
            return True
        except Exception as e:
            #log de error
            logger.error(e)
            
            #retornar fracaso
            return False
            
    def delete_client(self, id:int)->bool:
        #obtener la sesion
        with get_session() as session:
            #preparar la sentencia
            stmt = delete(Client).where(Client.id == id)
            
            #ejecutar la sentencia
            session.execute(stmt)
            
            #cerrar transaccion
            session.commit()
            
        #retornar exito
        return True
            