import csv
from ..modelos.notificacion import Notificacion

def registrar_notificacion(notificacion:Notificacion,filename='notificaciones.csv'):
    with open(filename, mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([notificacion.url,notificacion.estado])