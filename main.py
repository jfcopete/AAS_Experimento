import time
from fastapi import FastAPI, Request, Response,HTTPException
from contextlib import asynccontextmanager
from .modelos.notificacion import Notificacion
from .modelos.event_request import EventResponse
from .heartbeat.heartbeat import Heartbeat
from .heartbeat.tareas_periodicas import iniciar_tareas_periodicas,finalizar_tareas_periodicas
import httpx

heartbeat_handler = Heartbeat()
URL_BROKER = "http://localhost:8001"
URL_BROKER_SIGNUP_EVENT = URL_BROKER+"/publish"
USER_SIGN_UP="USER_SIGN_UP"
USER_SIGN_UP_RESPONSE="USER_SIGN_UP_RESPONSE"
HEARTBEAT="HEARTBEAT"
eventos_response = {}

@asynccontextmanager
async def lifespan(app:FastAPI):
    iniciar_tareas_periodicas()
    subscribe_response()
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

@app.post("/ms/signup/")
async def forward_request(request: Request):
    async with httpx.AsyncClient() as client:
        try:
            # Extraer información de la solicitud entrante
            body_bytes = await request.body()
            body_str = body_bytes.decode()  # Decodificar el cuerpo de la solicitud a una cadena
            headers = dict(request.headers)
            #cookies = request.cookies
            body_broker= {"event": USER_SIGN_UP, "data": body_str, "headers": headers}
            # Enviar la solicitud al servicio de destino incluyendo toda la información recibida
            response = await client.post(URL_BROKER_SIGNUP_EVENT, data=body_broker)
            # Devolver la respuesta del servicio de destino
            # ESPERAR POR EL EVENTO USER_SIGN_UP_RESPONSE
            id_event=response.json()["id"]
            while id_event not in eventos_response:
                time.sleep(1/60)
            response = Response(content=eventos_response[id_event]["body"], status_code=eventos_response[id_event]["status_code"], headers=eventos_response[id_event]["headers"])
            return response
        except httpx.HTTPError as e:
            # Manejar errores de conexión con el servicio de destino
            raise HTTPException(status_code=500, detail="Error al conectar con el servicio de destino")
        
@app.post("/ms/event_response")
async def event_response(evento: EventResponse):
    eventos_response[evento.id]= evento.dict()
    return {"message": "Event received"}
        

async def subscribe_response():
    async with httpx.AsyncClient() as client:
        try:
            body_broker = {"event": USER_SIGN_UP_RESPONSE, "callback_url": "http://localhost:8000/ms/event_response"}
            response = await client.post(url=URL_BROKER + "/subscribe", json=body_broker)
            if response.status_code == 200:
                print("Subscription successful")
                return {"message": "Subscription successful"}
            else:
                print("Subscription failed")
                return {"message": "Subscription failed"}
        except httpx.HTTPError as e:
            print(f"Error al conectar con el broker: {str(e)}")
            raise HTTPException(status_code=500, detail="Error al conectar con el broker")
        