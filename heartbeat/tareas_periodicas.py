import sys
import threading
import time
from app.heartbeat.heartbeat import verificar_servicios


event=threading.Event()


def iniciar_verificacion(event):
    print ("Thread de verificacion iniciado")
    while True:
        if(event.is_set()):
            break
            
        else:
            verificar_servicios()
            time.sleep(60)


def iniciar_tareas_periodicas():
    thread = threading.Thread(target=iniciar_verificacion, args=(event,))
    thread.start()
    
    
def finalizar_tareas_periodicas():
    event.set()