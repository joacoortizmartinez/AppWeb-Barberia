import os
from flask import Flask, render_template, request, url_for, redirect, jsonify, flash
from config import obtener_bd, cerrar_bd
from mysql.connector import Error
import mysql.connector
from clases.reservas import Reserva
from clases.user import User
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

app.secret_key = 'AguanteRiver912'


#---------------------------------------COMIENZO DE RUTAS--------------------------------------------------#
@app.route('/')
def inicio():
    return render_template('index.html')



@app.route('/reservar', methods=['GET', 'POST'])
def reserva():
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        sucursal = request.form['sucursal']
        fecha = request.form['fecha']
        hora = request.form['hora']

        reserva = Reserva(nombre, telefono, sucursal, fecha, hora)

        cone = obtener_bd()
        cursor = cone.cursor()
        
        query = "SELECT COUNT(*) FROM reservas WHERE fecha=%s AND hora=%s AND sucursal=%s;"
        values = (reserva.get_fecha(), reserva.get_hora(), reserva.get_sucursal())
        
        try:
            cursor.execute(query, values)
            result = cursor.fetchone()

            if result[0] == 0:
                query1 = "INSERT INTO reservas (nombre, telefono, sucursal, fecha, hora) VALUES (%s, %s, %s, %s, %s)"
                values1 =   (reserva.get_nombre(), reserva.get_telefono() ,reserva.get_sucursal(),reserva.get_fecha(), reserva.get_hora())
                cursor.execute(query1, values1)
                cone.commit()
                return "Reserva exitosa"
            else:
                return "La fecha y hora seleccionadas ya están ocupadas. Por favor, elija otra."
        
        except Error as e:
            print(f"Hubo un error: {e}")
            return "Error en la reserva. Por favor, intente nuevamente."
            
        finally:
            cerrar_bd(cone, cursor)

    else:
        horarios = obtener_horarios_disponibles()
        return render_template('usuarios/reserva.html', horarios=horarios)



def obtener_horarios_disponibles():
    cone = obtener_bd()
    cursor = cone.cursor(dictionary=True)
    cursor.execute('SELECT inicio, fin, intervalo FROM horarios LIMIT 1')
    horario = cursor.fetchone()
    cerrar_bd(cone, cursor)

    if horario:
        if isinstance(horario['inicio'], timedelta):
            inicio = (datetime.min + horario['inicio']).time()
        elif isinstance(horario['inicio'], str):
            inicio = datetime.strptime(horario['inicio'], '%H:%M').time()
        else:
            inicio = horario['inicio']

        if isinstance(horario['fin'], timedelta):
            fin = (datetime.min + horario['fin']).time()
        elif isinstance(horario['fin'], str):
            fin = datetime.strptime(horario['fin'], '%H:%M').time()
        else:
            fin = horario['fin']

        intervalo = int(horario['intervalo'])

        horarios = []
        while inicio < fin:
            horarios.append(inicio.strftime('%H:%M'))
            inicio = (datetime.combine(datetime.today(), inicio) + timedelta(minutes=intervalo)).time()
        return horarios
    return []



#-------------------------------------------HORARIOS-----------------------------------------#
@app.route('/configurar_horarios', methods=['GET', 'POST'])
def configurar_horarios():
    if request.method == 'POST':
        inicio = request.form['inicio']
        fin = request.form['fin']
        intervalo = int(request.form['intervalo'])
        
        
        cone = obtener_bd()
        cursor = cone.cursor() 
        
        
        query = "INSERT INTO horarios (inicio, fin, intervalo) VALUES (%s, %s, %s);"
        values = (inicio, fin, intervalo)
        
        try:
            cursor.execute(query, values)

        except Error as e:
            print (f" Hubo un error, disculpe")
        
        finally:
            cerrar_bd(cone, cursor)
        
        guardar_horarios(inicio, fin, intervalo)
        return redirect(url_for('inicio'))

    return render_template('admin/configuracion_horario.html')

def guardar_horarios(inicio, fin, intervalo):
    cone = obtener_bd()
    cursor = cone.cursor()  
    
    query = "INSERT INTO horarios (inicio, fin, intervalo) VALUES (%s, %s, %s);"
    values = (inicio, fin, intervalo)
        
    try:
        cursor.execute('DELETE FROM horarios')
        cursor.execute(query, values)
        cone.commit()

    except Error as e:
        print (f" Hubo un error, disculpe")
        
    finally:
            cerrar_bd(cone, cursor)


#----------------------------------reg--------------------------------------------------#
@app.route('/registro')
def registro():
    return render_template('admin/registro.html')


@app.route('/registrarse', methods=['GET', 'POST'])
def registrarse():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']

        hashed_password = generate_password_hash(password, method='sha256')
        
        user = User(usuario, hashed_password)
        query = "INSERT INTO barbero (usuario, password) VALUES (%s, %s);"
        values = (user.get_usuario(), user.get_password())

        
        cone = obtener_bd()
        cursor = cone.cursor()
        
        try:
            cursor.execute(query, values)
            cone.commit()
            flash('Usuario registrado exitosamente')
            return redirect(url_for('inicio'))
        
        except Error as e:
            flash(f'Error {e} ')
            
        finally:
            cerrar_bd(cone, cursor)
            

    return render_template('admin/registro.html')

#----------------------------------log--------------------------------------------------#


#----------------------------------FIN DE RUTAS--------------------------------------------------#

if __name__ == "__main__":
    app.run(debug=True)