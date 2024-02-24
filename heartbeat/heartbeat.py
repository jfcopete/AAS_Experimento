import logging
from datetime import datetime, timedelta
from ..modelos.notificacion import Notificacion
from .registro import registrar_notificacion

#Log Config
logging.basicConfig(filename='heartbeat.log',level=logging.INFO,format='%(asctime)s:%(message)s')
estado_servicios = {}

class Heartbeat:
    @staticmethod
    def procesar_notificacion(notificacion:Notificacion):
        registrar_notificacion(notificacion)
        
        #verificacion
        if notificacion.estado.lower()=="alive":
            logging.info(f"Hearbeat registrado para {notificacion.url} con estado {notificacion.estado}.")
            actualizar_estado_servicio(notificacion.url, notificacion.estado.lower())
        else:
            logging.error(f"Hearbeat registrado para {notificacion.url} con estado {notificacion.estado}.")
            actualizar_estado_servicio(notificacion.url, notificacion.estado.lower())


def actualizar_estado_servicio(url,estado):
    estado_servicios[url] = {'estado':estado,'timestamp':datetime.now()}
    
def verificar_servicios():
    if not estado_servicios:
        print ("No hay servicios para revisar")
        return
    
    for url,info in estado_servicios.items():
        if datetime.now() - info['timestamp'] > timedelta(minutes=1):
            estado_servicios[url] = {'estado':'dead','timestamp':datetime.now()}
            notificacion = Notificacion(url=url,estado='dead')
            Heartbeat.procesar_notificacion(notificacion)
            alertar_servicio_caido(url)
            
def alertar_servicio_caido(url):
    logging.info(f"Servicio {url} cayó.")
    print(f"ALERTA: Servicio {url} cayó.")