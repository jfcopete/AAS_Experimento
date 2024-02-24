from fastapi import FastAPI, Request, Response,HTTPException
from contextlib import asynccontextmanager
from .modelos.notificacion import Notificacion
from .heartbeat.heartbeat import Heartbeat
from .heartbeat.tareas_periodicas import iniciar_tareas_periodicas,finalizar_tareas_periodicas
import httpx

heartbeat_handler = Heartbeat()
URL_BROKER = "http://localhost:8001"

@asynccontextmanager
async def lifespan(app:FastAPI):
    iniciar_tareas_periodicas()
    yield
    finalizar_tareas_periodicas()
    


app = FastAPI(lifespan=lifespan)


"""
A function to handle the POST request to '/heartbeat' endpoint. It takes a 'notificacion' parameter of type 'Notificacion' and returns a dictionary with a success message.
"""
@app.post("/heartbeat")
async def endpoint_heartbeat(notificacion: Notificacion):
    # Utiliza la clase Heartbeat para procesar la notificación
    heartbeat_handler.procesar_notificacion(notificacion)
    
    return {"mensaje": "Heartbeat procesado y registrado con éxito"}

@app.get("/ms/gateway/")
async def gateway(request: Request):
    async with httpx.AsyncClient() as client:
        try:
            headers=dict(request.headers)
            cookies=request.cookies
            response = await client.get(URL_BROKER, headers=headers, cookies=cookies)
            return Response(content=response.content, status_code=response.status_code, headers=response.headers)
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500,detail="Error al conectar con el broker")

@app.post("/ms/gateway/")
async def forward_request(request: Request):
    async with httpx.AsyncClient() as client:
        try:
            # Extraer información de la solicitud entrante
            body_bytes = await request.body()
            body_str = body_bytes.decode()  # Decodificar el cuerpo de la solicitud a una cadena
            headers = dict(request.headers)
            cookies = request.cookies
            # Enviar la solicitud al servicio de destino incluyendo toda la información recibida
            response = await client.post(URL_BROKER, data=body_str, headers=headers, cookies=cookies)
            # Devolver la respuesta del servicio de destino
            return Response(content=response.content, status_code=response.status_code, headers=response.headers)
        except httpx.HTTPError as e:
            # Manejar errores de conexión con el servicio de destino
            raise HTTPException(status_code=500, detail="Error al conectar con el servicio de destino")