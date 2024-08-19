import mysql
import mysql.connector

DATABASE_CONFIG = {
        'host' : "localhost",
        'user' : "root",
        'password' : "",
        'database' : "barberia"
    }

def obtener_bd():
    cone = mysql.connector.connect(**DATABASE_CONFIG)
    return cone

def cerrar_bd(cone, cursor):
    cursor.close()
    cone.close()
        