import logging
from .database import Turn, get_session
from sqlalchemy import select, update, delete

#logger de repositorio
logger = logging.getLogger(__file__)

#repositorio de turnos
class TurnRepository:
    #operaciones
    def get_turns(self, page:int, per_page:int, client_id:int = 0):
        #contenedor
        turns = []
        
        #obtener la sesion
        with get_session() as session:
            #preparar el statement
            stmt = None
            
            if client_id:
                #obtener todos los turnos guardados
                stmt = select(Turn).where(Turn.client_id == client_id).limit(per_page).offset(per_page*page)
            else:
                #obtener todos los turnos guardados
                stmt = select(Turn).limit(per_page).offset(per_page*page)
            
            #ejecutar la query
            result = session.execute(stmt)
            
            #mapear turno
            turn = None
            for row in result.all():
                #obtener turnoss
                turn = row.tuple()[0]
                turn = turn.__dict__.copy()
                turn["start_hour"] = turn["start_hour"].strftime("%d/%m/%Y HH:MM:SS")
                turn["close_hour"] = turn["close_hour"] and turn["close_hour"].strftime("%d/%m/%Y HH:MM:SS")
                turn.pop('_sa_instance_state')
                
                #añadir diccionario
                turns.append(turn)
                
        return turns
        
    def get_turn(self, id:int)->dict|None:
        #contenedor
        turn = None
        
        #manejo de error
        try:
            #obtener la sesion
            with get_session() as session:
                #preparar sentencia
                stmt = select(Turn).where(Turn.id == id)
                
                #ejecutar sentencia
                res = session.execute(stmt)
                
                #obtener cliente
                turn = res.first().tuple()[0]
                
                #validar resultado
                if not turn:
                    raise Exception(f"turn {id} not found")
                
                turn = turn.__dict__.copy()
                turn["start_hour"] = turn["start_hour"].strftime("%d/%m/%Y HH:MM:SS")
                turn["close_hour"] = turn["close_hour"] and turn["close_hour"].strftime("%d/%m/%Y HH:MM:SS")
                turn.pop('_sa_instance_state')
        except Exception as e:
            #log de error
            logger.error(e)
            
        return turn
    
    def create_turn(self,data:dict)->int|None:
        #contenedor
        id = None
        
        #eliminar falso id
        if "id" in data.keys():
            data.pop("id")
        
        #manejo de error
        try:
            #obtener la sesion
            with get_session() as session:
                #preparar la sentencia
                trn = Turn(**data)
                
                #ejecutar la sentencia
                session.add(trn)
                session.commit()
                
                #obtener el id insertado
                id = trn.id
        except Exception as e:
            #log de error
            logger.error(e)
        
        #retornar el id
        return id
    
    def update_turn(self, id:int, data:dict)->bool:
        #eliminar falso id
        if "id" in data.keys():
            data.pop("id")
        
        #manejo de error
        try:
            #obtener la sesion
            with get_session() as session:
                #preparar la sentencia
                stmt = update(Turn).where(Turn.id == id).values(**data)
                
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
            
    def delete_turn(self, id:int)->bool:
        #obtener la sesion
        with get_session() as session:
            #preparar la sentencia
            stmt = delete(Turn).where(Turn.id == id)
            
            #ejecutar la sentencia
            session.execute(stmt)
            
            #cerrar transaccion
            session.commit()
            
        #retornar exito
        return True