
from flask import Flask, render_template, request, session, flash, redirect, url_for, jsonify, get_flashed_messages
from werkzeug.security import generate_password_hash, check_password_hash
import mysql
from config import obtener, cerrar 
from mysql.connector import Error
from functools import wraps
import requests
from datetime import datetime
import config

app = Flask(__name__)
app.secret_key= 'RiverVosSOSMIvida91218'



#_____________gestion de sesiones_______________#

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwrags):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwrags)
    return decorated_function




#____________________________________ Comienzo de rutas ___________________________#

@app.route('/', methods=['GET', 'POST'])
@login_required
def inicio():
    cone = obtener()
    cursor = cone.cursor(dictionary=True, buffered=True)
    
    id_user = session.get('user_id')
    ejercicios = []
    ejercicios_rutina = [] 
    
    query = "SELECT nombre, series, repes, peso, fecha FROM entrenamiento WHERE id_user = %s ORDER BY fecha DESC  LIMIT 5;"
    values = (id_user, )
    try:
        cursor.execute(query, values)
        ejercicios = cursor.fetchall()
        
        for ejercicio in ejercicios:
                        ejercicios_rutina.append({
                            "nombre": ejercicio['nombre'],
                            "series": ejercicio['series'],
                            "repes": ejercicio['repes'],
                            "peso": ejercicio['peso'],
                            "fecha": ejercicio['fecha']
                        })
        
    except Error as e:
            flash(f'Error {e}')
        
    finally:
        cerrar(cone, cursor)
            
    return render_template('index.html', ejercicios_rutina=ejercicios_rutina)



#_____________________________SIGN UP_________________________

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        user = request.form['user']
        mail = request.form['mail']
        password = request.form['pass']
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        cone = obtener()
        cursorfet = cone.cursor(dictionary=True)
        cursor = cone.cursor()
        
        queryfet = "SELECT * FROM usuarios WHERE usuario = %s;"
        valuesfet = (user, )
        
        query = "INSERT INTO usuarios (usuario, mail, password) VALUES (%s, %s, %s);"
        values = (user, mail, hashed_password)
        
        try:
            cursorfet.execute(queryfet, valuesfet)
            resultado = cursorfet.fetchone()
            
            if resultado is None:
                cursor.execute(query, values)
                cone.commit()
                
                queryy = "SELECT * FROM usuarios WHERE usuario = %s;"
                valuess = (user,)
                
                cursorr = cone.cursor(dictionary=True)
                cursorr.execute(queryy, valuess)
                users = cursorr.fetchone()
                
                print(users)
                
                if users is not None:
                    session['user_id'] = users['id_user']
                    session['username'] = users['usuario']
                
                flash('Usuario registrado')
                return redirect(url_for('configuracion_persona'))
            
            flash('Usuario ya existente')
        
        except Error as e:
            flash(f'Error {e}')
        
        finally:
            cerrar(cone, cursor)
            cursorfet.close()
            
    
    return render_template('sign in/sign.html')

#_______________________________LOGIN___________________________

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['usuario']
        password = request.form['Password']
    
        
        cone = obtener()
        cursor = cone.cursor(dictionary=True)
        
        query = "SELECT * FROM usuarios WHERE usuario = %s;"
        values = (user,)
        
        try:
            cursor.execute(query, values)
            users = cursor.fetchone()
            
            if users and isinstance(users, dict):
                if check_password_hash(users['password'], password):
                    session['user_id'] = users['id_user']
                    session['username'] = users['usuario']
                    
                    return redirect(url_for('inicio'))
                else:
                    flash('Usuario o contraseña incorrectos')
                    return redirect(url_for('login'))
            else:
                flash('Usuario o contraseña incorrectos')
                return redirect(url_for('login'))
                
                
        
        except Error as e:
            flash(f'Error{e}')
        
        finally:
            cerrar(cone, cursor)
        
        
    
    return render_template('login/login.html')


#______________________________First steeps_____________________
@app.route('/first-steeps', methods=['GET', 'POST'])
@login_required
def configuracion_persona():
    if request.method == 'POST':
        id_user = session.get('user_id')
        deseo = request.form['opciones']
        peso_actual = request.form['peso-actual']
        peso_deseado = request.form['peso-deseado']
        dias = request.form['dias']
        
        cone = obtener()
        cursor = cone.cursor()
        
        query = "INSERT INTO persona (id_user, deseo, peso_actual, peso_deseado, dias_en_gym) VALUES (%s, %s, %s, %s, %s);"
        values = (id_user, deseo, peso_actual, peso_deseado, dias)
        
        try:
            cursor.execute(query, values)
            cone.commit()
            return redirect(url_for('inicio'))
        
        except Error as e:
            flash(f'No se pudo{e}')
            
        finally:
            cerrar(cone, cursor)
    
    return render_template('config_personas/index.html')
    

#__________________________ Agregar Rutina_____________________
@app.route('/rutina', methods=['GET', 'POST'])
@login_required
def rutina():
    cone = obtener()
    cursor = cone.cursor(dictionary=True)
    
    query = "SELECT DISTINCT categoria FROM ejercicios;"
    
    ejercicios = []
    
    try:
        cursor.execute(query)
        Categorias = cursor.fetchall()
        
        nombredia = ''
        series = ''
        repes = ''
        ejercicio_seleccionado = ''
        
        if request.method == 'POST':
            categoria = request.form.get('opciones')
            
            nombredia = request.form.get('nombredia', '')
            series = request.form.get('series', '')
            repes = request.form.get('repes', '')
            ejercicio_seleccionado = request.form.get('ejercicios', '')
            cantidad_ejercicios = request.form.get('cantidadEjercicios', '0') 
            cantidad_ejercicios = int(cantidad_ejercicios)  
            id_us = session.get('user_id')
            
            
            query_rutina = "INSERT INTO rutinas (nombre, id_user) VALUES (%s, %s);"
            values_rutina = (nombredia, id_us)
            cursor.execute(query_rutina, values_rutina)
            cone.commit()
            
           
            cursor.execute("SELECT LAST_INSERT_ID() as id_rutina;")
            id_rutina = cursor.fetchone()['id_rutina']
            
            if categoria:
                querySelectEjercicios = "SELECT nombre_ej FROM ejercicios WHERE categoria = %s;"
                valuesSelectEjercicios = (categoria,)
                cursor.execute(querySelectEjercicios, valuesSelectEjercicios)
                ejercicios = cursor.fetchall()
                
            for i in range(cantidad_ejercicios):
                categoria = request.form.get(f'opciones_{i}')
                ejercicio_seleccionado = request.form.get(f'ejercicios_{i}')
                series = request.form.get(f'series_{i}')
                repes = request.form.get(f'repes_{i}')
                
                query_ejercicios = "INSERT INTO ejercicios_de_rutina (id_rutina, categoria, ejercicio_nombre, series, repes) VALUES (%s, %s, %s, %s, %s);"
                values_ejercicios = (id_rutina, categoria, ejercicio_seleccionado, series, repes)
                
                cursor.execute(query_ejercicios, values_ejercicios)
                
            cone.commit()
            flash('Agregaste la rutina')
            return redirect(url_for('inicio'))
        else:
            pass
            
    except Error as e:
        flash(f'No se pudo guardar la rutina: {e}')
        
    finally:
        cerrar(cone, cursor)
        
    return render_template('rutina/rutina.html', Categorias=Categorias, ejercicios=ejercicios, nombredia=nombredia, series=series, repes=repes, ejercicio_seleccionado=ejercicio_seleccionado)



@app.route('/buscar_ejercicios', methods=['POST'])
@login_required
def buscar_ejercicios():
    categoria = request.form.get('categoria')
    cone = obtener()
    cursor = cone.cursor(dictionary=True)
    
    try:
        querySelectEjercicios = "SELECT nombre_ej FROM ejercicios WHERE categoria = %s;"
        valuesSelectEjercicios = (categoria,)
        cursor.execute(querySelectEjercicios, valuesSelectEjercicios)
        ejercicios = cursor.fetchall()
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cerrar(cone, cursor)

    return jsonify(ejercicios)


#__________________________ Ver Rutina_____________________
@app.route('/mis-rutinas', methods=['GET', 'POST'])
@login_required
def ver_rutinas():
    nombres = []
    ejercicios_rutina = [] 
    id_us = session.get('user_id')
    
    cone = obtener()
    cursor = cone.cursor(dictionary=True, buffered=True)
    
    query = "SELECT nombre FROM rutinas WHERE id_user = %s;"
    values = (id_us, )
    rutina_seleccionada = None 
    fecha_seleccionada = None 
    try:
        cursor.execute(query, values)
        nombres = cursor.fetchall()
        
        if request.method == 'POST':
            session['rutina_seleccionada'] = request.form.get('rutina')
            session['fecha_seleccionada'] = request.form.get('fecha')

            rutina_seleccionada = session['rutina_seleccionada']
            fecha_seleccionada = session['fecha_seleccionada']
            nombre_rutina = request.form.get('rutina')
            if rutina_seleccionada:
                cursor_id = cone.cursor(dictionary=True, buffered=True)
                queryBuscar = "SELECT id_rutina FROM rutinas WHERE nombre = %s AND id_user = %s;"
                valuesBuscar = (nombre_rutina, id_us) 
                cursor_id.execute(queryBuscar, valuesBuscar)
                id_rutina_dicc = cursor_id.fetchone() 
                
                
                if id_rutina_dicc:
                    id_rutina = id_rutina_dicc['id_rutina']
                    cursor_ejercicios = cone.cursor(dictionary=True, buffered=True)
                    queryEjercicios = "SELECT categoria, ejercicio_nombre, series, repes FROM ejercicios_de_rutina WHERE id_rutina = %s;"
                    valuesEjercicios = (id_rutina, )
                    cursor_ejercicios.execute(queryEjercicios, valuesEjercicios)
                    resultado = cursor_ejercicios.fetchall()
                    
                    for ejercicio in resultado:
                        ejercicios_rutina.append({
                            "categoria": ejercicio['categoria'],
                            "ejercicio_nombre": ejercicio['ejercicio_nombre'],
                            "series": ejercicio['series'],
                            "repes": ejercicio['repes']
                        })
                    cursor_ejercicios.close()
                cursor_id.close()
    
    except Error as e:
        flash(f' error {e} ')
        
    finally:
        cerrar(cone, cursor)
        
    return render_template('rutina/ver_rutinas.html', nombres=nombres, ejercicios_rutina=ejercicios_rutina, rutina_seleccionada=rutina_seleccionada, fecha_seleccionada=fecha_seleccionada)


#__________________________ Eliminar _____________________
@app.route('/eliminar-rutina', methods=['GET', 'POST'])
@login_required
def eliminar_rutina():
    nombres = []
    id_us = session.get('user_id')
    
    cone = obtener()
    cursor = cone.cursor(dictionary=True, buffered=True)
    
    query = "SELECT nombre FROM rutinas WHERE id_user = %s;"
    values = (id_us, )
    try:
        cursor.execute(query, values)
        nombres = cursor.fetchall()
        if request.method=='POST':
            nombre_rutina = request.form.get('rutina')
            
            
            cursor_id = cone.cursor(dictionary=True, buffered=True)
            queryBuscar = "SELECT id_rutina FROM rutinas WHERE nombre = %s AND id_user = %s ;"
            valuesBuscar = (nombre_rutina, id_us)
            
            cursor_id.execute(queryBuscar, valuesBuscar)
            id_rutina_dicc = cursor_id.fetchone()
            
            if id_rutina_dicc:
                cursorEliminar = cone.cursor()
                id_rutina = id_rutina_dicc['id_rutina']
                
                queryEjercicios = "DELETE FROM ejercicios_de_rutina WHERE id_rutina = %s ;"
                valuesEjercicios = (id_rutina, )
                cursorEliminar.execute(queryEjercicios, valuesEjercicios)
                cone.commit()
                
                
                queryEliminar = "DELETE FROM rutinas WHERE nombre = %s AND id_user = %s ;"
                valuesEliminar = (nombre_rutina, id_us)
                cursorEliminar.execute(queryEliminar, valuesEliminar)
                cone.commit()
                flash('Rutina eliminada exitosamente')
                return redirect(url_for('inicio'))
            
            else:
                flash('No se encontró la rutina especificada')
                
                
        
    except Error as e:
        flash(f'Error {e} ')
        
    finally:
        cerrar(cone, cursor)
    return render_template('rutina/eliminar.html', nombres=nombres)





#__________________________ Marcar Rutina _____________________
@app.route('/rutina-hecha', methods=['GET', 'POST'])
@login_required
def rutina_hecha():
    nombres = []
    ejercicios_rutina = []
    id_us = session.get('user_id')

    cone = obtener()
    cursor = cone.cursor(dictionary=True, buffered=True)


    try:
        query = "SELECT nombre FROM rutinas WHERE id_user = %s;"
        values = (id_us, )
        cursor.execute(query, values)
        nombres = cursor.fetchall()
        

        if request.method == 'POST':
            nombre_rutina = request.form.get('rutina')
            if 'buscar_ejercicios' in request.form:
                queryBuscar = "SELECT id_rutina FROM rutinas WHERE nombre = %s AND id_user = %s;"
                valuesBuscar = (nombre_rutina, id_us)
                cursor.execute(queryBuscar, valuesBuscar)
                id_rutina_dicc = cursor.fetchone()
                

                if id_rutina_dicc:
                    id_rutina = id_rutina_dicc['id_rutina']

                    queryEjercicios = "SELECT ejercicio_nombre FROM ejercicios_de_rutina WHERE id_rutina = %s;"
                    valuesEjercicios = (id_rutina, )
                    cursor.execute(queryEjercicios, valuesEjercicios)
                    resultado = cursor.fetchall()

                    for ejercicio in resultado:
                        ejercicios_rutina.append({
                            "ejercicio_nombre": ejercicio['ejercicio_nombre']
                        })
                        
                        
            elif 'guardar_progreso' in request.form:
                for nombre in request.form:
                    if nombre.startswith('series_'):
                        ejercicio_nombre = nombre.split('series_')[1]
                        series = request.form.get(f'series_{ejercicio_nombre}')
                        repes = request.form.get(f'repes_{ejercicio_nombre}')
                        peso = request.form.get(f'peso_{ejercicio_nombre}')
                        fecha = request.form.get('fecha')
                        fecha_formateada = datetime.strptime(fecha, '%Y-%m-%d').date()

                        queryEjercitacion = """
                            INSERT INTO entrenamiento (nombre, series, repes, peso, fecha, id_user)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        valuesEjercitacion = (ejercicio_nombre, series, repes, peso, fecha_formateada, id_us)
                        cursor.execute(queryEjercitacion, valuesEjercitacion)
                        
                cone.commit()
                flash('Progreso guardado!')

    except Error as e:
        cone.rollback()
        flash(f'Error: {e}')
        
    finally:
        cerrar(cone, cursor)

    return render_template('ejercitacion/ejercitacion.html', nombres=nombres, ejercicios_rutina=ejercicios_rutina)



#__________________________ Cerrar sesion _____________________
@app.route("/cerrar-sesion", methods=["POST"])
def cerrar_sesion():
    session.clear()
    return redirect(url_for('login'))


#____________________________________ Fin de rutas ___________________________#

if __name__ == "__main__":
    app.run(debug=True)