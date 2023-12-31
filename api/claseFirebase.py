# Importa la configuracion de firebase para poder inicializar la aplicacion Firebase
from firebaseConfig import config
# Importa la libreria pyrebase para poder inicializar la aplicacion Firebase
from pyrebase import pyrebase
# Se define la clase Firebase, que es una clase contenida por la clase JodApp
# Para manejar la base de datos en tiempo real y la autenticacion
class Firebase():
    def __init__(self):
        #Inicializa la aplicacion de firebase mediante la configuracion especifica
        self.firebase = pyrebase.initialize_app(config)
        #Atributo para gestionar la autenticacion de los usuarios
        self.autenticacion = self.firebase.auth()
        #Atributo para gestionar la base de datos en tiempo real
        self.baseDeDatosTR = self.firebase.database()
    
    def getFirebase(self):
        return self.firebase
    
    def setFirebase(self, otraConfig):
        self.firebase = pyrebase.initialize_app(otraConfig)
        self.autenticacion = self.firebase.auth()
        self.baseDeDatosTR = self.firebase.database()

    # Metodo privado para la validar que el atributo sea distinto (ejemplo: para ingresar nombres de usuario distintos)
    # Si ya existe ese valor de atributo, devolvera False, es decir no es distinto
    # Si no existe, devolvera True, es decir es distinto y valido
    def __validacionAtributoDistinto(self, tipo, nombreAtributo, valorAtributoNew):
        listaTipo = self.baseDeDatosTR.child(tipo).get()
        distinto = True
        try:
            for diccionario in listaTipo.each():
                if(diccionario.val()[nombreAtributo]==valorAtributoNew):
                    distinto = False
                    break
        except:
            print("Aun no existe")
        return distinto
    
    # Metodo privado para validar que el ID sea distinto
    # Validacion de ID distinto (ejemplo: para ingresar DNIs distintos)
    # Si ya existe ese ID, devolvera False, es decir no es distinto
    # Si no existe, devolvera True, es decir es distinto y valido
    def __validacionIDDistinto(self, tipo, idObjeto):
        listaDiccionarios = self.baseDeDatosTR.child(tipo).get()
        distinto = True
        try:
            for diccionario in listaDiccionarios.each():
                if(diccionario.key()==idObjeto):
                    distinto = False
                    break
        except:
            print("Aun no existe")
        return distinto

    # autenticacion
    # El siguiente metodo publico se utiliza para validar que no exista el correo y guardarlo si es valido al crear el objeto usuario
    def authCrearUsuario(self, correo, contra):
        try:
            usuario = self.autenticacion.create_user_with_email_and_password(correo, contra)
            return usuario
        except:
            #correo ya existente
            return False
        
    # autenticacion
    # El siguiente metodo publico se utiliza para iniciar sesion
    # Si el correo y contrasenna son correctos, entonces devuelve al usuario
    # Por si luego quiere cambiar el correo o contrasenna
    def authIniciarSesion(self, correo, contra):
        try:
            usuario = self.autenticacion.sign_in_with_email_and_password(correo, contra)
            return usuario
        except:
            return None
    # El siguiente metodo publico permite al usuario iniciar sesion mediante su nombre de usuario y la contrasenna
    # Primero encuentra el correo mediante el nombre de usuario
    def authIniciarSesionUser(self, user, contra):
        usuarios = self.baseDeDatosTR.child("Usuarios").get()
        correo=""
        for usuario in usuarios.each():
            if(usuario.val()['user']==user):
                correo=usuario.val()['correo']
                dni = usuario.key()
                break
        # Veo si realmente la contrasenna es correcta
        if(correo!=""):
            usuarioValido = self.authIniciarSesion(correo, contra)
            # Esto quiere decir que el usuario inicio sesion correctamente
            if(usuarioValido!=None):
                print(dni)
                return dni
        # Esto quiere decir que no pudo iniciar sesion, user o contrasenna incorrectos
        return False

    # baseDeDatosTR
    # El siguiente metodo publico se utiliza para guardar cualquier objeto en formato JSON
    # Con tipo especificamos en que seccion se guardara, por ejemplo Usuarios
    # Con id especificamos como sera reconocido, en el caso de Personas mediante el DNI
    # diccio seria el objeto ya convertido en diccionario para ser guardado
    def guardarDiccionario(self, tipo, diccio, idObjeto=None, atributoDistinto=None, atributoDistinto2=None):
        if(idObjeto is None):
            # Si el idObjeto es None, quiere decir que su id se genera automaticamente en Firebase, como para Fiesta, Concierto o Match
            # Si no es None, quiere decir que seria un id generado desde el codigo, por ejemplo, el caso de Personas (Usuario, Artista, Jugador, etc)
            self.baseDeDatosTR.child(tipo).push(diccio)
            return True
        # Primero verifica que el ID sea distinto a uno ya existente (ejemplo DNI)
        if(self.__validacionIDDistinto(tipo, idObjeto)):
            if(atributoDistinto is None):
                # Esto quiere decir que se tiene un Artista o un Jugador, 
                # por lo que no tenemos que validar atributos distintos, solo el DNI
                self.baseDeDatosTR.child(tipo).child(idObjeto).set(diccio)
                return True
            # En el caso de que exista atributoDistinto, entonces quiere decir que se tiene un Usuario
            # El atributoDistinto guarda el nombre del atributo que debe ser distinto a uno ya guardado (ejemplo user)
            valorAtributoNuevo = diccio[atributoDistinto]
            # El atributoDistinto2 guarda el nombre de otro atributo que debe ser distinto a uno ya guardado (ejemplo correo)
            valorAtributoNuevo2 = diccio[atributoDistinto2]
            if((self.__validacionAtributoDistinto(tipo, atributoDistinto, valorAtributoNuevo))&(self.__validacionAtributoDistinto(tipo, atributoDistinto2, valorAtributoNuevo2))):
                # Si el valor del atributo es realmente distinto, se guarda en la base de datos
                self.baseDeDatosTR.child(tipo).child(idObjeto).set(diccio)
                # Luego que se devuelve True se puede crear el usuario con el metodo authCrearUsuario
                return True
        return False


    # baseDeDatosTR
    # El siguiente metodo publico se utiliza para editar cualquier diccionario en formato JSON
    # Con tipo especificamos en que seccion se encuentra el diccionario a editar, por ejemplo Usuarios
    # Con id especificamos que diccionario sera editado, en el caso de Personas seria con el DNI
    # Diccio guardaria todos los nombres de los atributos a editar, junto con sus nuevos valores 
    # usuario es un parametro opcional, podria ser un usuario que accedio a la autenticacion de firebase
    # o nos podria indicar mediante la palabra 'lista' que debemos modificar una lista, lo cual nos lleva
    # una serie de pasos extra para poder annadirle un nuevo valor
    def editarAtributos(self, tipo, idObjeto, diccio, usuario=""):
        distinto = True
        if(tipo=="Usuarios"):
            if "user" in diccio:
                distinto = self.__validacionAtributoDistinto(tipo, "user", diccio['user'])
            if "correo" in diccio:
                distinto = self.__validacionAtributoDistinto(tipo, "correo", diccio['correo'])
        if(distinto):
            
            if((usuario!="")&(usuario!="lista")):
                # Esto es en el caso de que se haya podido autenticar anteriormente para modificar el correo
                usuario.update_email(diccio['correo'])
            if(usuario=="lista"):
                diccioViejo = self.baseDeDatosTR.child(tipo).child(idObjeto).get().val()
                claves = list(diccio.keys())
                print(claves)
                clave = claves[0]
                try:
                    # En este caso existe la lista en el diccionario
                    listaVieja = diccioViejo[clave]
                    listaVieja.append(diccio[clave])
                    diccioViejo[clave] = listaVieja
                    diccio = diccioViejo
                except Exception:
                    # En este caso aun no, entonces la creamos
                    listaNueva = [diccio[clave]]
                    diccioViejo[clave] = listaNueva
                    diccio = diccioViejo
            self.baseDeDatosTR.child(tipo).child(idObjeto).update(diccio)
        # Si es True quiere decir que se modifico
        # Si es False quiere decir que no se pudo modificar pq era igual a uno ya existente en el caso de user y correo
        return distinto

    # baseDeDatosTR
    # El siguiente metodo publico se utiliza para editar un ID (por ejemplo DNI)
    # Con tipo especificamos en que seccion se encuentra el diccionario a editar, por ejemplo Usuarios
    # Con idObjeto especificamos que clave sera editada y reemplazada por idNuevo 
    def editarID(self, tipo, idObjeto, idNuevo):
        #True quiere decir que logra cambiarse, False que no pudo pq es igual a uno existente
        idCambiado = self.__validacionIDDistinto(tipo, idNuevo)
        if(idCambiado):
            referenciaVieja = self.baseDeDatosTR.child(tipo).child(idObjeto)
            datos = referenciaVieja.get().val()
            self.baseDeDatosTR.child(tipo).child(idObjeto).remove()
            self.baseDeDatosTR.child(tipo).child(idNuevo).set(datos)
            #ID cambiado con exito
        return idCambiado
    
    # baseDeDatosTR
    # Mediante este metodo publico se obtiene el ID del objeto recien creado
    # Primero se debe pasar como argumento al objeto convertido en diccionario
    # Tambien la seccion que podria ser Fiestas, Conciertos, etc
    def obtenerID(self, diccio, tipo):
        listaDiccio = self.baseDeDatosTR.child(tipo).get().val()

        for clave in listaDiccio:
            if listaDiccio[clave] == diccio:
                return clave
        return None
    # El siguiente metodo publico obtiene todos los diccionarios mediante el tipo (ejemplo Usuarios) y su clave (ejemplo "dni")
    def obtenerTodosDictConKey(self, tipo, clave='id'):
        # Obtiene los diccionarios en formato Pyre
        listaDictPyre = self.baseDeDatosTR.child(tipo).get()
        listaDict = []
        for diccio in listaDictPyre:
            diccioAux = diccio.val()
            # Se guardan los childs como el valor del ID o DNI, dependiendo de que datos se quieren obtener
            diccioAux[clave] = diccio.key()
            listaDict.append(diccioAux)
        return listaDict

    # El siguiente metodo publico recupera todos los diccionarios 
    # En el caso de que se quiera obtener diccionarios con un valor especifico
    # Y tambien en el caso de que se quiera saber si ese valor existe dentro de alguna lista de algun diccionario
    def recuperarTodosDict(self, tipo, valor=None, asistidos=False):
        # Se obtienen todos los elementos del "tipo"
        diccionarios = self.baseDeDatosTR.child(tipo).get().val()
        # Ahora se recuperan todos los elementos en un diccionario que las claves son los ids, y los valores son los diccionarios del "tipo"
        if diccionarios is None:
            diccionarios = {}
        else:
            if(valor is not None):
                listaNueva = []
                # Recorre cada diccionario
                for clave, diccionario in diccionarios.items():
                    if(asistidos):
                        listaIntegrantes = diccionario.get('asistentes', [])
                        if valor in listaIntegrantes:
                            # Para saber si asiste al evento
                            diccio = diccionario
                            diccio['id'] = clave
                            listaNueva.append(diccio)
                    else:
                        if valor in diccionario.values():
                            # Si el valor esta en el diccionario, lo agrega a la lista
                            # Para saber si es el creador del evento
                            diccio = diccionario
                            diccio['id'] = clave
                            listaNueva.append(diccio)
                # Reemplaza la lista de diccionarios con la nueva
                diccionarios = listaNueva
        return diccionarios
    
    # baseDeDatosTR
    # El siguiente metodo publico se utiliza para obtener muchos diccionarios mediante una lista de IDs
    # En el caso de que la lista sea de un solo ID, devolvera solo un diccionario
    # Este es un dict Pyre, eso quiere decir que tiene .value()=valores y .key()=id/child/dni
    def obtenerListaDiccionarios(self, tipo, listaIDs):
        listaDiccio = self.baseDeDatosTR.child(tipo).get()
        listaCoincidencias = []
        for idValor in listaIDs:
            for diccio in listaDiccio.each():
                if(diccio.key()==idValor):
                    listaCoincidencias.append(diccio)
                    break
        return listaCoincidencias

    # baseDeDatosTR
    # El siguiente metodo se utiliza para eliminar un diccionario mediante el ID
    # Con tipo especificamos en que seccion se encuentra el diccionario a eliminar, por ejemplo Usuarios
    # Con idObjeto especificamos que diccionario sera eliminado
    def eliminarDiccionario(self, tipo, idObjeto, contra=None):
        # Si tipo es Usuarios, se debe eliminar tambien su correo de la autenticacion de Firebase
        if(tipo=="Usuarios"):
            # Obtenemos el diccionario del usuario
            diccio = self.obtenerListaDiccionarios(tipo, [idObjeto])
            diccio = diccio[0]
            diccio = diccio.val()
            # Como la contrasenna no se guarda en la base de datos, se debe pasar como argumento
            userFire = self.authIniciarSesion(diccio['correo'], contra)
            self.autenticacion.delete_user_account(userFire['idToken'])
        if(tipo=="Fiestas" or tipo=="Conciertos" or tipo=="Matchs"):
            # Obtenemos el diccionario del evento
            diccio = self.obtenerListaDiccionarios(tipo, [idObjeto])
            diccio = diccio[0]
            diccio = diccio.val()
            asistentes = diccio['asistentes']
            anfitrion = diccio['anfitrion']
            try:
                # Eliminamos el id del evento de la lista de eventos creados del usuario anfitrion
                self.eliminarID("Usuarios", anfitrion, 'listaEventos', idObjeto)
            except:
                print("Ya ha sido eliminado")
            for asistente in asistentes:
                try:
                    # Eliminamos el id del evento de la lista de asistencias de cada usuario asistente
                    self.eliminarID("Usuarios", asistente, 'listaEventosAsistidos', idObjeto)
                except:
                    print("Ya ha sido eliminado")
        # Finalmente se elimina el objeto de la base de datos
        self.baseDeDatosTR.child(tipo).child(idObjeto).remove()

    # baseDeDatosTR
    # El siguiente metodo se utiliza para eliminar un ID en una lista que esta dentro de un diccionario
    # Con tipo especificamos en que seccion se encuentra el ID a eliminar, por ejemplo Usuarios
    # Con idObjeto especificamos en que diccionario sera eliminado ese ID
    def eliminarID(self, tipo, idObjeto, claveLista, idEliminar):
        # Se obtiene el diccionario viejo
        diccionario = self.baseDeDatosTR.child(tipo).child(idObjeto).get().val()
        # Se elimina el ID de la lista
        diccionario[claveLista].remove(idEliminar)
        print(diccionario[claveLista])
        # Se vuelve a guardar el diccionario nuevo
        self.baseDeDatosTR.child(tipo).child(idObjeto).set(diccionario)
