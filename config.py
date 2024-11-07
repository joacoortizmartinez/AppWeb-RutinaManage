import mysql
import mysql.connector

DATABASE_CONFIG = {
    'host' : 'localhost',
    'user' : 'root',
    'password' : '',
    'database' : 'gym'
    }

def obtener():
    return mysql.connector.connect(**DATABASE_CONFIG)

def cerrar(cone, cursor):
    if cursor:
        cursor.close()
    if cone:
        cone.close()

