
from flask import Flask, render_template, request, flash, redirect, url_for
from claseFirebase import Firebase
from claseUsuario import Usuario
from claseFiesta import Fiesta
from claseBanda import Banda
from claseArtista import Artista
from claseJugador import Jugador
from claseEquipo import Equipo
import matplotlib.pyplot as plt
import io, base64
import matplotlib.figure as figure
import matplotlib.backends.backend_agg as backend_agg
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
#from claseConcierto import Concierto
#from claseMatch import Match
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
        self.app.route('/creacionEvento', methods=['POST'])(self.creacionEvento)
        self.app.route('/crearEvento', methods=['POST'])(self.crearEvento)
        self.app.route('/verListaEventos', methods=['POST'])(self.verListaEventos)
        self.app.route('/verListaDeSusEventos', methods=['POST'])(self.verListaDeSusEventos)
        # Estas rutas vuelven a redirigir a creacionEvento, una vez creado un Artista, Banda, Jugador o Equipo
        self.app.route('/crearArtista', methods=['POST', 'GET'])(self.crearArtista)
        self.app.route('/crearBanda', methods=['POST', 'GET'])(self.crearBanda)
        self.app.route('/crearJugador', methods=['POST', 'GET'])(self.crearJugador)
        self.app.route('/crearEquipo', methods=['POST', 'GET'])(self.crearEquipo)
        self.app.route('/verFiesta', methods=['POST'])(self.verFiesta)
        self.app.route('/accionEvento', methods=['POST'])(self.accionEvento)
    
    def __graficoBarrasMasAsistentes(self, listaOrdenada):
        plt.figure()
        # listaOrdenada es una lista de diccionarios que alberga 'c'=cant de asistentes 'f'=nombre de la fiesta
        cantidadesAsistentes = [fiesta['c'] for fiesta in listaOrdenada[:10]]
        nombresFiestas = [fiesta['f'] for fiesta in listaOrdenada[:10]]

        plt.bar(nombresFiestas, cantidadesAsistentes)
        plt.xlabel('Nombre de la Fiesta')
        plt.ylabel('Cantidad de Asistentes')
        plt.title('Cantidad de Asistentes por Fiesta')
        # Se obtiene la figura actual
        fig = plt.gcf()

        output = io.BytesIO()
        # Guarda la figura en el objeto BytesIO
        fig.savefig(output, format='png')

        # objeto de io.BytesIO que contiene los datos de la imagen
        imagenCodificada = base64.b64encode(output.getvalue()).decode('utf-8')
        return imagenCodificada

    def __graficoTortaMasAsistentes(self, listaOrdenada):
        plt.figure
        asistentes = []
        nombreFiesta = []
        #listaOrdenada es una lista de diccionarios que alberga 'c'=cant de asistentes 'f'=nombre de la fiesta
        for nombreCant in listaOrdenada:
            asistentes.append(nombreCant['c'])
            nombreFiesta.append(nombreCant['f'])
        plt.pie(asistentes, labels=nombreFiesta, autopct="%0.1f %%")
        plt.title(f"Fiestas Con Más Asistentes")
        plt.legend()
        plt.axis("equal")
        # Se obtiene la figura actual
        fig = plt.gcf()

        output = io.BytesIO()
        # Guarda la figura en el objeto BytesIO
        fig.savefig(output, format='png')

        # objeto de io.BytesIO que contiene los datos de la imagen
        imagenCodificada = base64.b64encode(output.getvalue()).decode('utf-8')
        return imagenCodificada

    def accionEvento(self):
        accion = request.form.get('accion')
        datos = request.form.to_dict()
        #flash(datos)
        idFiesta = datos.get('idEvento')
        dni = datos.get('dni')
        print(idFiesta)
        listaFiestaDictPyre = self.firebase.obtenerListaDiccionarios("Fiestas", [idFiesta])
        listaFiestaDictPyre = listaFiestaDictPyre[0]
        fiestaDict = listaFiestaDictPyre.val()
        fiestaDict['id'] = idFiesta
        fiestaObj = self.__crearObjetosFiesta([fiestaDict])
        fiestaObj = fiestaObj[0]
        if(accion=='asistir'):
            fiestaObj.setAsistente(dni, self.firebase)
        elif(accion == "noAsistir"):
            fiestaObj.eliminarAsistente(dni, self.firebase)
        elif(accion=='editar'):
            nombre = datos.get('nombre')
            descripcion = datos.get('descripcion')
            fecha = datos.get('fecha')
            fechaFin = datos.get('fechaFin')
            # Descripcion de la ubicacion
            ubicacion = datos.get('ubicacionD')
            latitud = datos.get('latitud')
            longitud = datos.get('longitud')
            precio = datos.get('precio')
            capacidad = datos.get('capacidad')
            edadMin = datos.get('edadMin')
            edadMax = datos.get('edadMax')
            vestimenta = datos.get('vestimenta')
            categoria = datos.get('categoria')
            bar = datos.get('bar')
            conservadora = datos.get('conservadora')
            if(nombre!=fiestaObj.getNombre() and nombre!=""):
                fiestaObj.setNombre(nombre, self.firebase)
            if(descripcion!=fiestaObj.getDescripcion() and descripcion!=""):
                fiestaObj.setDescripcion(descripcion, self.firebase)
            if(fecha!=fiestaObj.getFecha()):
                fiestaObj.setFecha(fecha, self.firebase)
            if(fechaFin!=fiestaObj.getFechaFin()):
                fiestaObj.setFechaFin(fechaFin, self.firebase)
            
            fiestaObj.setUbicacion([latitud, longitud, ubicacion], self.firebase)

            if(precio!=fiestaObj.getPrecio() and precio!=""):
                fiestaObj.setPrecio(precio, self.firebase)
            if(capacidad!=fiestaObj.getCapacidad() and capacidad!=""):
                fiestaObj.setCapacidad(capacidad, self.firebase)
            if(edadMin<edadMax):
                fiestaObj.setRango([edadMin, edadMax], self.firebase)
            if(vestimenta!=fiestaObj.getVestimenta() and vestimenta!=""):
                fiestaObj.setVestimenta(vestimenta, self.firebase)
            if(categoria!=fiestaObj.getCategoria() and categoria!=""):
                fiestaObj.setCategoria(categoria, self.firebase)
            if(bar!=fiestaObj.getBar()):
                fiestaObj.setBar(bar, self.firebase)
            if(conservadora!=fiestaObj.getConservadora()):
                fiestaObj.setConservadora(conservadora, self.firebase)
            flash("La fiesta ha sido modificada con los valores nuevos.", 'evento')
        elif(accion=='eliminar'):
            self.firebase.eliminarDiccionario("Fiestas", idFiesta)
            flash("La fiesta ha sido eliminada de la base de datos", 'evento')
        usuarioValido = self.firebase.obtenerListaDiccionarios("Usuarios", [dni])
        usuarioValido = usuarioValido[0]
        # usuarioValido seria el usuario de tipo diccionario
        usuarioValido = usuarioValido.val()
        # usuarioObjeto seria el usuario de tipo objeto
        # Pone al child como una clave valor mas para la creacion del objeto Usuario
        usuarioValido['dni'] = dni
        # Crea el usuario a partir del diccionario
        usuarioObjeto = Usuario(**usuarioValido)
        # Vuelve a la pantalla de inicio
        context = { 'server_time': self.__formatoServidorTiempo(), 'dni':dni, 'usuario': usuarioValido, 'usuarioObjeto': usuarioObjeto}
        return render_template('jodappInicio.html', context=context)

    def verFiesta(self):
        idFiesta = request.form.get('id')
        dni = request.form.get('dni')
        creador = request.form.get('creador')
        print("creador: ddd", creador)
        asistencia = "NO"
        #creador = "NO"
        if(creador=="SI"):
            listaFiestas = self.firebase.recuperarTodosDict("Fiestas", dni)
        elif(creador=="NO"):
            listaFiestas = self.firebase.recuperarTodosDict("Fiestas", dni, True)
            if(listaFiestas==[]):
                listaFiestas = self.firebase.obtenerTodosDictConKey('Fiestas')
        elif(creador=="NOOO"):
            listaFiestas = self.firebase.obtenerTodosDictConKey('Fiestas')
        listaObjFiestas = self.__crearObjetosFiesta(listaFiestas)
        fiestaObj = ""
        anfitrion = ""
        for fiesta in listaObjFiestas:
            if(fiesta.getID()==idFiesta):
                anfitrion = fiesta.getAnfitrion()
                #if(anfitrion == dni):
                #    creador = "SI"
                listaAsis = fiesta.getAsistentes()
                if dni in listaAsis:
                    asistencia = "SI"
                fiestaObj = fiesta
                break
        #fiestaPyre = self.firebase.obtenerListaDiccionarios("Fiestas", [idFiesta])
        
        dictFiesta = fiestaObj.objetoToDiccionario()
        dictFiesta['id'] = idFiesta
        #listaDatosFiestas = self.__listaDatosEventos(listaObjFiestas)
        context = { 'server_time': self.__formatoServidorTiempo(), 'fiesta':dictFiesta, 'evento':"Fiesta", 'dni':dni, 'dniCreador':anfitrion, 'asistencia':asistencia}
        return render_template('jodappVerEvento.html', context=context)

    def crearEvento(self):
        diccioDatos = request.form.to_dict()
        evento = diccioDatos.get('tipoEvento')
        ubicacionDescrip = diccioDatos.get('ubicacionD')
        ubicacionLatitud = diccioDatos.get('latitud')
        ubicacionLongitud = diccioDatos.get('longitud')
        nombre = diccioDatos.get('nombre')
        descripcion = diccioDatos.get('descripcion')
        fecha = diccioDatos.get('fecha')
        fechaFin = diccioDatos.get('fechaFin')
        precio = diccioDatos.get('precio')
        capacidad = diccioDatos.get('capacidad')
        edadMin = diccioDatos.get('edadMin')
        edadMax = diccioDatos.get('edadMax')
        dni = request.form.get('dni')
        if edadMin is None or edadMax is None:
            condiRango = False
        else:
            condiRango = edadMin>edadMax
        condiEvento = not ubicacionDescrip or not ubicacionLatitud or not ubicacionLongitud or not nombre or not descripcion or not fecha or not fechaFin or not precio or not capacidad or not edadMin or not edadMax or condiRango
        if(evento=='Fiesta'):
            vestimenta = diccioDatos.get('vestimenta')
            categoria = diccioDatos.get('categoria')
            #bar = diccioDatos.get('bar')
            #artistas = request.form.get('listaArtistaIds').split(',')
            # debo ver que error tiene las listaBandaIds diccioDatos.get('listaBandaIds').split(',')
            bandas = request.form.get('listaBandaIds').split(',')
            #flash(bandas, 'evento')
            condiEvento = condiEvento or not vestimenta or not categoria
        elif(evento=='Concierto'):
            print("Concierto")
            bandas = request.form.get('listaBandaIds').split(',')
            condiEvento= condiEvento or not vestimenta or not categoria or bandas==['']
        elif(evento=='Match'):
            equipos = request.form.get('listaEquipoIds')
            condiEvento = condiEvento or equipos==[]
            print("Match")
        
        if(condiEvento):
            # Se muestran los errores con flash
            if(not ubicacionDescrip):
                flash("La descripción de la ubicación no puede estar vacía.", 'evento')
            if(not ubicacionLatitud or not ubicacionLongitud):
                flash("Debe seleccionar una ubicación en el mapa.", 'evento')
            if(not nombre):
                flash("El nombre del evento no puede estar vacío.", 'evento')
            if(not descripcion):
                flash("La descripción del evento no puede estar vacía.", 'evento')
            if(not fecha):
                flash("Debe seleccionar una fecha de inicio.", 'evento')
            if(not fechaFin):
                flash("Debe seleccionar una fecha de finalización.", 'evento')
            if(not precio):
                flash("El precio debe ser 0 o mayor.", 'evento')
            if(not capacidad):
                flash("La capacidad no puede estar vacía.", 'evento')
            if(not edadMin):
                flash("La edad mínima no puede estar vacía", 'evento')
            if(not edadMax):
                flash("La edad máxima no puede estar vacía", 'evento')
            if(condiRango):
                flash("La edad mínima no puede ser mayor a la edad máxima", 'evento')
            if(evento=='Fiesta'):
                if(not vestimenta):
                    flash("La vestimenta no puede estar vacía.", 'evento')
                if(not categoria):
                    flash("La categoria no puede estar vacía.", 'evento')
            elif(evento=='Concierto'):
                print("errores concierto")
            elif(evento=='Match'):
                print("errores match")
        else:
            # Se puede crear el evento
            diccioDatos['rango'] = [edadMin, edadMax]
            del diccioDatos['edadMin']
            del diccioDatos['edadMax']
            
            diccioDatos['anfitrion'] = dni
            diccioDatos['ubicacion'] = [ubicacionLatitud, ubicacionLongitud, ubicacionDescrip]
            if(evento=='Fiesta'):

                if(bandas!=['']):
                    diccioDatos['bandas'] = diccioDatos['listaBandaIds']
                else:
                    diccioDatos['bandas'] = None
                diccioFiesta = diccioDatos
                del diccioFiesta['dni']
                del diccioFiesta['listaBandaIds']
                del diccioFiesta['tipoEvento']
                del diccioFiesta['ubicacionD']
                del diccioFiesta['usuario']
                del diccioFiesta['usuarioObjeto']
                # Se guarda en la bd firebase
                self.firebase.guardarDiccionario("Fiestas", diccioFiesta)
                flash(f"¡Felicidades, la fiesta {nombre} se creo exitosamente!", 'evento')
            elif(evento=='Concierto'):
                print("crear concierto")
                #conciertoNuevo = Concierto(**diccioDatos)
            elif(evento=='Match'):
                print("crear match")
                #matchNuevo = Match(**diccioDatos) 1234
        dictGrupo, dictPerso = self.listGrupoIntegrantes(evento)
        usuarioDict = diccioDatos.get('usuario')
        usuarioObj = diccioDatos.get('usuarioObj')
        context = { 'server_time': self.__formatoServidorTiempo(), 'usuario':usuarioDict, 'dni':dni, 'usuarioObjeto':usuarioObj, 'evento':evento, 'dictGrupo':dictGrupo, 'dictPerso': dictPerso }
        return render_template('jodappCrearEvento.html', context=context)


    def __obtenerDictConIds(self, listaDictPyre, clave):
        listaDict = []
        for dictPyre in listaDictPyre:
            dictNuevo = dictPyre.val()
            dictNuevo[clave] = dictPyre.key()
            listaDict.append(dictNuevo)
        return listaDict
    
    def __crearObjetosArtista(self, listaDict):
        listaArtista = []
        for diccio in listaDict:
            artistaNuevo = Artista(**diccio)
            listaArtista.append(artistaNuevo)
        return listaArtista
    
    def __crearObjetosBanda(self, listaDict):
        listaBanda = []
        for diccio in listaDict:
            print(diccio['integrantes'])
            #artistas = self.firebase.obtenerListaDiccionarios('Artistas', diccio['integrantes'])
            #listaArtista = self.__crearObjetosArtista(artistas)
            #diccio['integrantes'] = listaArtista
            listaArtista = []
            for integrante in diccio['integrantes']:
                artista = Artista(**integrante)
                listaArtista.append(artista)
            diccio['integrantes'] = listaArtista
            bandaNueva = Banda(**diccio)
            listaBanda.append(bandaNueva)
        return listaBanda

    def __crearObjetosFiesta(self, listaDict):
        listaFiesta = []
        for diccio in listaDict:
            if 'bandas' in diccio:
                #flash(diccio['bandas'])
                bandas = self.firebase.obtenerListaDiccionarios('Bandas', diccio['bandas'])
                #flash(bandas)
                listaBanda = self.__crearObjetosBanda(bandas)
                diccio['bandas'] = listaBanda
            fiestaNueva = Fiesta(**diccio)
            listaFiesta.append(fiestaNueva)
        return listaFiesta

    def crearBanda(self):
        diccioDatos = request.form.to_dict()
        
        evento = diccioDatos.get('tipoEvento')
        # Recupera el nombre y el genero, sino se ingresaron devuelven None
        nombre = diccioDatos.get('nombreB')
        genero = diccioDatos.get('generoB')
        # Recupera la lista de artistas de la sesión
        # si listaArtistaIds no existe en el diccionario diccioDatos, devuelve una lista vacia
        print(request.form.get('listaArtistaIds'))
        artistas = request.form.get('listaArtistaIds').split(',')
        condi = not nombre or not genero or artistas==['']
        if(condi):
            if(not nombre):
                flash("El nombre de la banda no puede estar vacío", 'banda')
            if(not genero):
                flash("El género de la banda no puede estar vacío.", 'banda')
            if(artistas==['']):
                flash("La banda debe tener al menos un artista agregado.", 'banda')
        else:
            #print(f"ARTISTAS:: {artistas}")
            artistasDictPyre = self.firebase.obtenerListaDiccionarios("Artistas", artistas)
            artistasDict = self.__obtenerDictConIds(artistasDictPyre, "dni")
            artistasObj = self.__crearObjetosArtista(artistasDict)
            #print(lista[0].key())
            #print(lista[1].val())
            diccioBanda = {'nombre':nombre, 'genero':genero, 'integrantes':artistasObj}
            # Se crea un objeto de tipo Banda 
            bandaNueva = Banda(**diccioBanda)
            diccioBanda['integrantes'] = artistasDict
            self.firebase.guardarDiccionario("Bandas", diccioBanda)
            flash(f"¡Felicidades, la banda {nombre} se creo exitosamente!", 'banda')

        dictGrupo, dictPerso = self.listGrupoIntegrantes(evento)
        usuarioDict = diccioDatos.get('usuario')
        usuarioObj = diccioDatos.get('usuarioObj')
        context = { 'server_time': self.__formatoServidorTiempo(), 'usuario':usuarioDict, 'usuarioObjeto':usuarioObj, 'evento':evento, 'dictGrupo':dictGrupo, 'dictPerso': dictPerso }
        return render_template('jodappCrearEvento.html', context=context)



    def crearArtista(self):
        diccioDatos = request.form.to_dict()
        evento = diccioDatos.get('tipoEvento')
        dni = diccioDatos.get('dni')
        nombre = diccioDatos.get('nombre')
        apellido = diccioDatos.get('apellido')
        edad = diccioDatos.get('edad')
        talento = diccioDatos.get('talento')
        condi = not dni or not nombre or not apellido or not edad or not talento
        if(condi):
            if(not nombre):
                flash("El nombre del artista no puede estar vacío.", 'artista')
            if(not dni):
                flash("El DNI del artista no puede estar vacío.", 'artista')
            if(not apellido):
                flash("El apellido del artista no puede estar vacío.", 'artista')
            if(not edad):
                flash("La edad del artista no puede estar vacía.", 'artista')
            if(not talento):
                flash("El talento del artista no puede estar vacío.", 'artista')
        else:
            artistaNew = Artista(**diccioDatos)
            diccioArtista = artistaNew.objetoToDiccionario()
            self.firebase.guardarDiccionario("Artistas", diccioArtista, dni)
            flash(f"¡Felicidades, el artista {nombre} se creo exitosamente!", 'artista')

        dictGrupo, dictPerso = self.listGrupoIntegrantes(evento)
        usuarioDict = diccioDatos['usuario']
        usuarioObj = diccioDatos['usuarioObj']
        context = { 'server_time': self.__formatoServidorTiempo(), 'usuario':usuarioDict, 'usuarioObj':usuarioObj, 'evento':evento, 'dictGrupo':dictGrupo, 'dictPerso': dictPerso }
        return render_template('jodappCrearEvento.html', context=context)


    def crearJugador(self):
        evento = request.form['tipoEvento']
        diccioDatos = request.form.to_dict()
        self.creacionEvento(evento)

    def crearEquipo(self):
        evento = request.form['tipoEvento']
        self.creacionEvento(evento)

    def __obtenerUsuarioDictObj(self):
        # Obtenemos el usuario diccionario
        usuarioDict = request.form['usuario']
        # Obtenemos el usuario objeto
        usuarioObj = request.form['usuarioObjeto']
        return [usuarioDict, usuarioObj]

    def __contextLista(self):
        listaDictObj = self.__obtenerUsuarioDictObj()
        context = { 'server_time': self.__formatoServidorTiempo(), 'usuarioDict':listaDictObj[0], 'usuarioObj':listaDictObj[1]}
        return context

    # Serian los eventos creados y eventos asistidos del usuario
    def verListaDeSusEventos(self):
        dni = request.form['dni']

        listaFiestas = self.firebase.recuperarTodosDict("Fiestas", dni)
        listaObjFiestas = self.__crearObjetosFiesta(listaFiestas)
        listaDatosFiestas = self.__listaDatosEventos(listaObjFiestas)

        listaFiestasAsis = self.firebase.recuperarTodosDict("Fiestas", dni, True)
        listaObjFiestasAsis = self.__crearObjetosFiesta(listaFiestasAsis)
        listaDatosFiestasAsis = self.__listaDatosEventos(listaObjFiestasAsis)


        listaConciertos = self.firebase.recuperarTodosDict("Conciertos", dni)
        listaObjConciertos = self.__crearObjetosFiesta(listaConciertos)
        listaDatosConciertos = self.__listaDatosEventos(listaObjConciertos)

        listaConciertosAsis = self.firebase.recuperarTodosDict("Conciertos", dni, True)
        listaObjConciertosAsis = self.__crearObjetosFiesta(listaConciertosAsis)
        listaDatosConciertosAsis = self.__listaDatosEventos(listaObjConciertosAsis)


        listaMatchs = self.firebase.recuperarTodosDict("Matchs", dni)
        listaObjMatchs = self.__crearObjetosFiesta(listaMatchs)
        listaDatosMatchs = self.__listaDatosEventos(listaObjMatchs)
        
        listaMatchsAsis = self.firebase.recuperarTodosDict("Matchs", dni, True)
        listaObjMatchsAsis = self.__crearObjetosFiesta(listaMatchsAsis)
        listaDatosMatchsAsis = self.__listaDatosEventos(listaObjMatchsAsis)

        #for fiesta in listaObjFiestas:
        #    flash(fiesta.mostrar())
        #    break

        #flash(listaFiestas)
        context = { 'server_time': self.__formatoServidorTiempo(), 'dni':dni, 'listasFiestas':listaDatosFiestas, 'listasFiestasAsis':listaDatosFiestasAsis}
        return render_template('jodappListaDeSusEventos.html', context=context)
    
    # Objetos para el HTML
    def __listaDatosEventos(self, listaEventosObjetos):
        listaDatosEventos = []
        for evento in listaEventosObjetos:
            idEvento = evento.getID()
            cadena = evento.mostrarLista()
            listaEvento = cadena.split("$&$")
            # Esto servira para ser mostrado en el html
            listaEvento.insert(0, idEvento)
            listaDatosEventos.append(listaEvento)
        return listaDatosEventos
    
    # Serian todos los eventos que existen
    def verListaEventos(self):
        usuarioDict = request.form['usuario']
        usuarioObj = request.form['usuarioObjeto']
        dni = request.form['dni']
        
        #listaConciertos = self.firebase.recuperarTodosDict("Conciertos")
        #listaMatchs = self.firebase.recuperarTodosDict("Matchs")

        listaFiestas = self.firebase.obtenerTodosDictConKey('Fiestas')
        listaObjFiestas = self.__crearObjetosFiesta(listaFiestas)
        listaDatosFiestas = self.__listaDatosEventos(listaObjFiestas)
        # Ordena la lista segun la cantidad de asistentes que esta guardado en el indice 7
        listaDatosFiestas  = sorted(listaDatosFiestas , key=lambda i: i[7])
        # Crea una nueva lista de diccionarios que se utiliza para los graficos de barra y torta
        listaOrdenada = []
        for fiesta in listaDatosFiestas:
            diccioAux = {'c':fiesta[7], 'f':fiesta[1]}
            listaOrdenada.append(diccioAux)
        listaDatosFiestas  = sorted(listaDatosFiestas , key=lambda i: i[7], reverse=True)
        # Solo el top 10 de las fiestas mas asistidas
        listaOrdenada = listaOrdenada[-10:]
        # Establecemos 'Agg' como el backend de matplotlib. 'Agg' es un backend basado en raster 
        # que no requiere una interfaz gráfica de usuario. 
        # Para evitarnos errores porque generamos graficos desde el servidor
        matplotlib.use('Agg')
        imagenCodificadaTorta = self.__graficoTortaMasAsistentes(listaOrdenada)
        imagenCodificadaBarras = self.__graficoBarrasMasAsistentes(listaOrdenada)
        context = { 'server_time': self.__formatoServidorTiempo(), 'dni':dni, 'listasFiestas':listaDatosFiestas, 'graficoTorta':imagenCodificadaTorta, 'graficoBarra': imagenCodificadaBarras}
        return render_template('jodappListaEventos.html', context=context)

    def listGrupoIntegrantes(self, eventoSeleccionado):
        if(eventoSeleccionado!="Match"):
            # Si es Fiesta o Concierto se guardan bandas y artistas
            dictGrupo = self.firebase.recuperarTodosDict("Bandas")
            dictPerso = self.firebase.recuperarTodosDict("Artistas")
        else:
            # Si es Match se guardan equipos y jugadores
            dictGrupo = self.firebase.recuperarTodosDict("Equipos")
            dictPerso = self.firebase.recuperarTodosDict("Jugadores")
        return [dictGrupo, dictPerso]

    def creacionEvento(self, actualizacion=False):

        if(actualizacion!=False):
            # En el caso de que sea distinta de falsa, quiere decir que tiene el evento seleccionado
            eventoSeleccionado = actualizacion
        else:
            # Obtenemos el tipo de evento que se selecciono para crear (Fiesta, Concierto, Match)
            # En el caso de que la actualizacion sea falsa
            eventoSeleccionado = request.form['tipoEvento']
        dictGrupo, dictPerso = self.listGrupoIntegrantes(eventoSeleccionado)
        usuario = request.form.get('usuario')
        usuarioObjeto = request.form.get('usuarioObjeto')
        dni = request.form.get('dni')
        context = { 'server_time': self.__formatoServidorTiempo(), 'dni':dni, 'usuario':usuario, 'usuarioObjeto':usuarioObjeto, 'evento':eventoSeleccionado, 'dictGrupo':dictGrupo, 'dictPerso': dictPerso }
        return render_template('jodappCrearEvento.html', context=context)

    def __formatoServidorTiempo(self):
        servidorTiempo = time.localtime()
        return time.strftime("%I:%M:%S %p", servidorTiempo)
    
    def home(self):
        # PRUEBAS #
        #usuarioObjeto = Usuario(41414888, "Miguel Dario", "Coronel", "25", "mdarioc1998@gmail.com", "Dario07")
        #usuarioValido = self.firebase.authIniciarSesionUser("Dario07", "A123456789B")
        #authIniciarSesionUser devuelve el dni
        #usuarioValido = self.firebase.obtenerListaDiccionarios("Usuarios", [usuarioValido])
        #usuarioValido = usuarioValido[0]
        # usuarioValido seria el usuario de tipo diccionario
        #usuarioDiccio = usuarioValido.val()
        #print(usuarioDiccio)

        #usuarioObjeto = Usuario(41414888, "Miguel Dario", "Coronel", "25", "mdarioc1998@gmail.com", "Dario07", listaEventos, listaAmigos, listaEAsis)
        # Por si la cago para volver a guardarlo
        #usuarioDiccio = usuarioObjeto.objetoToDiccionario()
        #usuarioValido = self.firebase.guardarDiccionario("Usuarios", usuarioDiccio, 40000000)
                
        #usuarioValido = self.firebase.authIniciarSesionUser("Dario07", "A123456789B")
        #usuarioObjeto.setNombre("Miguel Dario", self.firebase)
        #self.firebase.eliminarID("Usuarios", 41414888, 'listaEventos', 'dfdsfe34243')
        #usuarioObjeto.eliminarEvento("Fiestas", "dfdsfe34243", self.firebase)

        #usuarioObjeto.setAmigo(10000001, self.firebase)
        #usuarioObjeto2 = Usuario(10000001, "Azul Yanel", "Coronel", "20", "coro", "Azu14")
        #usuarioObjeto2.setAmigo(41414888, self.firebase)

        #usuarioObjeto.eliminarAmigo(10000001, self.firebase)
        #usuarioObjeto2.eliminarAmigo(41414888, self.firebase)
        #usuarioObjeto.eliminarAmigo(10000001, self.firebase)
        #usuarioObjeto.setEdad("25", self.firebase)
        #usuarioObjeto.setDNI(41414888, self.firebase)
        ############    ######
        #lista = (self.firebase.obtenerListaDiccionarios("Artistas", ["10000004", "10000005"]))
        #print(lista[0].key())
        #print(lista[1].val()) 1234
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
                flash("¡Felicidades! Ingresaste con éxito")
                dni = usuarioValido
                usuarioValido = self.firebase.obtenerListaDiccionarios("Usuarios", [usuarioValido])
                usuarioValido = usuarioValido[0]
                # usuarioValido seria el usuario de tipo diccionario
                usuarioValido = usuarioValido.val()
                # usuarioObjeto seria el usuario de tipo objeto
                #print(usuarioValido)
                # Pone al child como una clave valor mas para la creacion del objeto Usuario
                usuarioValido['dni'] = dni
                #flash(usuarioValido)
                # Crea el usuario a partir del diccionario
                usuarioObjeto = Usuario(**usuarioValido)
                #flash(usuarioObjeto)
                #print(usuarioObjeto.getAsistencias())
                context = { 'server_time': self.__formatoServidorTiempo(), 'dni':dni, 'usuario': usuarioValido, 'usuarioObjeto': usuarioObjeto}
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
                diccioUsuario = {'dni':dni, 'nombre':nombre, 'apellido':apellido, 'edad':edad, 'correo':correo, 'user':user}
                usuarioObjeto = Usuario(**diccioUsuario)
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
