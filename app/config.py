import mysql
import mysql.connector

DATABASE_CONFIG = {
        'host' : "localhost",
        'user' : "root",
        'password' : "",
        'database' : "barberia"
    }

def obtener_bd():
    conex = mysql.connector.connect(**DATABASE_CONFIG)
    return conex

def cerrar_bd(conex, cursor):
    if conex.is_connected():
        cursor.close()
        conex.close()
        