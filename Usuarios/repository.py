import logging
from database import User, get_session
from sqlalchemy import select

#logger de repositorio
logger = logging.getLogger(__file__)

#repositorio de usuario
class UserRepository:
    #operaciones
    def get_user_by_name(self, nombre_usuario:str)->dict|None:
        #contenedor
        user = None

        #manejo de error
        try:
            #obtener la sesion
            with get_session() as session:
                #preparar sentencia
                stmt = select(User).where(User.nombre_usuario == nombre_usuario)

                #ejecutar sentencia
                res = session.execute(stmt).first()

                #validar resultado
                if res:
                    #obtener usuario
                    user = res.tuple()[0].__dict__.copy()
                    user.pop('_sa_instance_state')
        except Exception as e:
            #log de error
            logger.error(e)

        return user

    def create_user(self, data:dict)->int|None:
        #contenedor
        id = None

        #manejo de error
        try:
            #obtener la sesion
            with get_session() as session:
                #preparar la sentencia
                user = User(**data)

                #ejecutar la sentencia
                session.add(user)
                session.commit()

                #obtener el id insertado
                id = user.id
        except Exception as e:
            #log de error
            logger.error(e)

        #retornar el id
        return id