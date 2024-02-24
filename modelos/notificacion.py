from pydantic import BaseModel,HttpUrl

class Notificacion(BaseModel):
    url:HttpUrl
    estado:str