import os
from flask import Flask, render_template, request, url_for, redirect, jsonify, flash, session
from mysql.connector import Error
import mysql.connector
from clases.reservas import Reserva
from clases.user import User
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import mysql
import mysql.connector

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

app.secret_key = 'AguanteRiver912'


#------------------------------Decorador Verificar Sesión de Usuario-------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


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



#----------------------------------reg--------------------------------------------------#
@app.route('/registro')
def registro():
    return render_template('admin/registro.html')


@app.route('/registrarse', methods=['GET', 'POST'])
def registrarse():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        rol = request.form['rol']
        
        hashed_password = generate_password_hash(password, method='sha256')
        
        user = User(usuario, hashed_password, rol)
        query1 = "INSERT INTO barbero (usuario, password, rol) VALUES (%s, %s, %s);"
        values1 = (user.get_usuario(), user.get_password(), rol)

        query = "select usuario from barbero where usuario = %s"
        values = (user.get_usuario(),)
        
        cone = obtener_bd()
        cursor = cone.cursor()
        cursorsele = cone.cursor(dictionary=True)
        try:
            cursorsele.execute(query, values)
            resul = cursorsele.fetchone()
            
            if resul == None:
                cursor.execute(query1, values1)
                cone.commit()
                flash('Usuario registrado exitosamente')
                return redirect(url_for('login'))
            
            flash('Usuario existente')
            return redirect(url_for('registrarse'))

        
        except Error as e:
            flash(f'Error {e} ')
            
        finally:
            cerrar_bd(cone, cursor)
            cursorsele.close()
            

    return render_template('admin/registro.html')

#----------------------------------log--------------------------------------------------#
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        
        cone = obtener_bd()
        cursor = cone.cursor(dictionary=True)
        
        query = 'SELECT * FROM barbero WHERE usuario = %s'
        values = (usuario,)
        
        try:
            cursor.execute(query, values)
            users = cursor.fetchall()
            
            
            if users:
                user = users[0]
                
                if check_password_hash(user['password'], password):
                    session['user_id'] = user['id_baarbero']
                    session['username'] = user['usuario']
                    session['rol'] = user['rol']
                    flash('Inicio de sesión exitoso')
                    return redirect(url_for('admin_inicio'))
                else:
                    flash('Usuario/pass incorrectas')
                    return redirect(url_for('login'))
            else:
                flash('Usuario/pass  incorrectas')
                return redirect(url_for('login'))
        
        except Error as e:
            print(f'Error: {e}')
            flash('Error en la base de datos')
            return redirect(url_for('login'))
        
        finally:
            cerrar_bd(cone, cursor)
            
    return render_template('admin/login.html')


#----------------------------------admin inicio---------------------------------------------#
@app.route('/admin-inicio', methods=['GET', 'POST'])
@login_required
def admin_inicio():
    if session.get('rol') != 'adyn':
        flash('Acceso denegado: No tienes permisos suficientes.', 'danger')
        return redirect(url_for('inicio'))
    return render_template('admin/admin.html')




#-------------------------------------------HORARIOS-----------------------------------------#
@app.route('/configurar-horarios', methods=['GET', 'POST'])
@login_required
def configurar_horarios():
    if session.get('rol') != 'adyn':
        flash('Acceso denegado: No tienes permisos suficientes.', 'danger')
        return redirect(url_for('inicio'))
    
    if request.method == 'POST':
        inicio = request.form['inicio']
        fin = request.form['fin']
        intervalo = int(request.form['intervalo'])
        
        
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
        
        return redirect(url_for('admin_inicio'))

    return render_template('admin/configuracion_horario.html')


#-------------------------------------------VER RESERVAS-----------------------------------------#
@app.route('/ver-reservas', methods=['GET', 'POST'])
@login_required
def ver_reservas():
    resultado = []
    fecha = None
    
    if session.get('rol') != 'adyn':
        flash('Acceso denegado: No tienes permisos suficientes.')
        return redirect(url_for('inicio'))
    
    if request.method == 'POST':
        fecha = request.form['fecha']

        cone = obtener_bd()
        cursor = cone.cursor(dictionary=True)
        query = "SELECT * FROM reservas WHERE fecha = %s"

        try:
            cursor.execute(query, (fecha,))
            data = cursor.fetchall()                          
            
            for fila in data:        
                contenido = { 
                            "id": fila['id'], 
                            "nombre": fila['nombre'], 
                            "telefono": fila['telefono'],
                            "sucursal": fila['sucursal'],
                            "fecha": fila['fecha'],
                            "hora": fila['hora'],
                            }  #11
                resultado.append (contenido)
        
        except Error as e:
            return f"No se pudo obtener {e}"
        
        finally:
            cerrar_bd(cone, cursor)
                        
    return render_template('admin/ver_reservas.html', reservas=resultado, fecha_seleccionada=fecha)
    
    



#----------------------------------FIN DE RUTAS--------------------------------------------------#

if __name__ == "__main__":
    app.run(debug=True)