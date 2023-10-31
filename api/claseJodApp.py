#from flask import Flask, render_template, make_response
#import time
#from firebaseConfig import config
#from pyrebase import pyrebase

#firebase=pyrebase.initialize_app(config)
#autenticacion = firebase.auth()
#bd = firebase.database()


#app = Flask(__name__)

#def format_server_time():
#  server_time = time.localtime()
#  return time.strftime("%I:%M:%S %p", server_time)

#@app.route('/')
#def home():
#    context = { 'server_time': format_server_time() }
#    return render_template('index.html', context=context)

#@app.route('/login')
#def login():
#    return render_template('login.html')

#@app.route('/signup')
#def signup():
#    return render_template('signup.html')

#if __name__ == '__main__':
#    app.run()


from flask import Flask, render_template, make_response, request, flash, redirect, url_for
from claseFirebase import Firebase
from claseUsuario import Usuario
import time

class JodApp:
    def __init__(self):
        self.firebase = Firebase()
        self.context = { 'server_time': self.__formatoServidorTiempo() }
        self.app = Flask(__name__)
        self.app.secret_key = "holaMundo"
        self.app.route('/')(self.home)
        self.app.route('/login')(self.login)
        self.app.route('/signup', methods=['POST', 'GET'])(self.signup)
        self.app.route('/registrarte', methods=['POST', 'GET'])(self.registrarte)
        self.app.route('/iniciarSesion', methods=['POST', 'GET'])(self.iniciarSesion)
        self.app.route('/crearEvento', methods=['POST'])(self.crearEvento)

    def crearEvento(self):
        # Obtenemos el tipo de evento que se selecciono para crear
        eventoSeleccionado = request.form['tipoEvento']
        context = { 'server_time': self.__formatoServidorTiempo() }
        return render_template('jodappCrearEvento.html', context=context)

    def __formatoServidorTiempo(self):
        servidorTiempo = time.localtime()
        return time.strftime("%I:%M:%S %p", servidorTiempo)
    
    def home(self):
        context = { 'server_time': self.__formatoServidorTiempo() }
        return render_template('index.html', context=context)

    def login(self):
        context = { 'server_time': self.__formatoServidorTiempo() }
        return render_template('login.html', context=context)

    def signup(self):
        context = { 'server_time': self.__formatoServidorTiempo() }
        return render_template('signup.html', context=context)
    
    def iniciarSesion(self):
        user = request.form.get('username')
        contra = request.form.get('password')
        if not user or not contra:
            if(not user):
                flash("El usuario no puede estar vacío.")
            if(not contra):
                flash("La contraseña no puede estar vacía.")
        else:
            usuarioValido = self.firebase.authIniciarSesionUser(user, contra)
            if(usuarioValido!=False):
                # Se obtiene el usuario en formato diccionario
                # usuarioValido seria el usuario de tipo diccionario
                # usuarioObjeto seria el usuario de tipo objeto
                dni = usuarioValido['dni']
                nombre = usuarioValido['nombre']
                apellido = usuarioValido['apellido']
                edad = usuarioValido['edad']
                correo = usuarioValido['correo']
                listaEventos = usuarioValido['listaEventos']
                listaAmigos = usuarioValido['listaAmigos']
                listaEventosAsistidos = usuarioValido['listaEventosAsistidos']
                usuarioObjeto = Usuario(dni, nombre, apellido, edad, correo, user, listaEventos, listaAmigos, listaEventosAsistidos)
                flash("¡Felicidades! Ingresaste con éxito")
                usuarioValido = self.firebase.obtenerListaDiccionarios("Usuarios", [usuarioValido])
                usuarioValido = usuarioValido[0]
                usuarioValido = usuarioValido.val()
                print(usuarioValido)
                context = { 'server_time': self.__formatoServidorTiempo(), 'usuario': usuarioValido, 'usuarioObjeto':usuarioObjeto }
                return render_template('jodappInicio.html', context=context)
            
            flash("Usuario y/o contraseña incorrectos")
        # Vuelve a la pantalla de signup con el respectivo mensaje flash
        context = { 'server_time': self.__formatoServidorTiempo() }
        return redirect(url_for('login', context=context))
        
    def registrarte(self):
        dni = request.form.get('dni')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        edad = request.form.get('edad')
        correo = request.form.get('correo')
        user = request.form.get('username')
        contra = request.form.get('password')
        contra2 = request.form.get('password2')
        condi = not dni or not nombre or not apellido or not edad or not correo or not user or not contra or not contra2
        if condi:
        #Uno o mas entradas vacias
            if(not dni):
                flash("El DNI no puede estar vacío.")
            if(not nombre):
                flash("El nombre no puede estar vacío.")
            if(not apellido):
                flash("El apellido no puede estar vacío.")
            if(not edad):
                flash("La edad no puede estar vacía.")
            if(not correo):
                flash("El correo no puede estar vacío.")
            if(not user):
                flash("El usuario no puede estar vacío.")
            if(not contra or not contra2):
                flash("Las contraseñas no pueden estar vacías y deben ser iguales.")
        else:
        #Las entradas estan llenas
            bande=False
            if(contra==contra2):
                # Instancia de la clase Usuario
                usuarioObjeto = Usuario(dni, nombre, apellido, edad, correo, user)
                # Lo convierto en diccionario
                usuarioDiccio = usuarioObjeto.objetoToDiccionario()
                # Verifico si es un usuario valido con la base de datos
                usuarioValido = self.firebase.guardarDiccionario("Usuarios", usuarioDiccio, dni, 'user', 'correo')
                if(usuarioValido):
                    #("El usuario se guardo en la bd, por lo tanto es valido, para crear un usuarioAuth (que guarde su correo y contrasenna para autenticarse)")
                    usuarioAuth = self.firebase.authCrearUsuario(correo, contra)
                    if(usuarioAuth!=False):
                        # Deberia poner un mensaje de Felicidades, usuario creado
                        flash("¡Felicidades! Tu usuario ha sido registrado")
                        context = { 'server_time': self.__formatoServidorTiempo() }
                        return render_template('index.html', context=context)
                    bande=True
                else:
                    bande=True
            else:
                flash("Las contraseñas no coinciden.")
            if(bande):
                flash("Usuario y/o correo ya existentes.")

        # Vuelve a la pantalla de registro con el respectivo mensaje flasj
        context = { 'server_time': self.__formatoServidorTiempo() }
        return redirect(url_for('signup', context=context))

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    JodApp().run()
