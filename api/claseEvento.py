# Importa la clase Ubicacion, ya que es una clase contenida por Evento
from claseUbicacion import Ubicacion
# Define una nueva clase llamada Evento
# Es una clase abstracta (no se realiza instancia de esta)
# Es una clase base para las clases Fiesta, Concierto y Grupo
class Evento():
    # En el constructor se encuentra **kwargs 
    # Es el parámetro que nos permite crear objetos a partir de pasarle un diccionario con todos los valores de los atributos
    # Como la base de datos de Firebase guarda en formato diccionario, es una forma más sencilla de volver a crear los objetos
    def __init__(self, **kwargs):
        # El ID se genera desde la base de datos de Firebase al guardar el objeto,
        # Con el metodo setID se guarda el valor del ID
        self.__id = kwargs.get('id', "")
        self.__nombre = kwargs.get('nombre')
        self.__fecha = kwargs.get('fecha')
        # Una instancia de la clase Ubicacion
        # Es una relacion de composicion con Evento siendo contenedora, y Ubicacion contenida
        # El parametro ubicacion es una lista con los argumentos necesarios de latitud, longitud y descripcion
        ubicacion = kwargs.get('ubicacion')
        self.__ubicacion = Ubicacion(ubicacion[0], ubicacion[1], ubicacion[2])
        self.__precio = kwargs.get('precio')
        self.__descripcion = kwargs.get('descripcion')
        # DNI del usuario que creo el evento
        self.__anfitrion = kwargs.get('anfitrion')
        # Si el objeto se crea por primera vez sera una lista vacia
        # En cambio, si ya existe en la base de datos
        # se pasara la lista con los IDs de los asistentes
        self.__asistentes = kwargs.get('asistentes', [])
        self.__fechaFin = kwargs.get('fechaFin')
        self.__capacidad = kwargs.get('capacidad')
        self.__capacidad = int(self.__capacidad)
        self.__rango = kwargs.get('rango')


    # Getters para obtener atributos del evento
    def getID(self):
        return self.__id
    
    def getNombre(self):
        return self.__nombre
    
    def getFecha(self):
        return self.__fecha
    
    def getUbicacion(self):
        return self.__ubicacion
    
    def getPrecio(self):
        return self.__precio
    
    def getDescripcion(self):
        return self.__descripcion
    
    def getAnfitrion(self):
        return self.__anfitrion
    
    def getFechaFin(self):
        return self.__fechaFin
    
    def getAsistentes(self):
        return self.__asistentes
    
    def getCapacidad(self):
        return self.__capacidad
    
    def getRango(self):
        return self.__rango

    # Setters para establecer atributos del evento
    def setID(self, valor):
        self.__id = valor
    # Los siguientes Setters utilizan la instancia de la clase Firebase 
    # Se utiliza para guardar los nuevos valores a la base de datos de firebase
    # Mediante el ID del evento en cuestion y el tipo que sera asignado en las clases hijas de Evento
    def setNombre(self, valor, firebase, tipo):
        if(firebase.editarAtributos(tipo, self.getID(), {'nombre': valor})):
            self.__nombre = valor

    def setFecha(self, valor, firebase, tipo):
        if(firebase.editarAtributos(tipo, self.getID(), {'fecha': valor})):
            self.__fecha = valor

    def setUbicacion(self, valor, firebase, tipo):
        if(firebase.editarAtributos(tipo, self.getID(), {'ubicacion': valor})):
            self.__ubicacion = Ubicacion(valor[0], valor[1], valor[2])

    def setPrecio(self, valor, firebase, tipo):
        if(firebase.editarAtributos(tipo, self.getID(), {'precio': valor})):
            self.__precio = valor

    def setDescripcion(self, valor, firebase, tipo):
        if(firebase.editarAtributos(tipo, self.getID(), {'descripcion': valor})):
            self.__descripcion = valor

    def setAnfitrion(self, valor, firebase, tipo):
        if(firebase.editarAtributos(tipo, self.getID(), {'anfitrion': valor})):
            self.__anfitrion = valor

    def setAsistente(self, valor, firebase, tipo):
        if(firebase.editarAtributos(tipo, self.getID(), {'asistentes': valor}, "lista")):
            firebase.editarAtributos("Usuarios", valor, {'listaEventosAsistidos': self.getID()}, "lista")
            self.__asistentes.append(valor)

    def setFechaFin(self, valor, firebase, tipo):
        if(firebase.editarAtributos(tipo, self.getID(), {'fechaFin': valor})):
            self.__fechaFin = valor

    def setCapacidad(self, valor, firebase, tipo):
        if(firebase.editarAtributos(tipo, self.getID(), {'capacidad': valor})):
            self.__capacidad = valor

    def setRango(self, valor, firebase, tipo):
        if(firebase.editarAtributos(tipo, self.getID(), {'rango': valor})):
            self.__rango = valor

# Método privado para obtener la capacidad actual
    def __capacidadActual(self):
        return self.__capacidad-self.cantidadAsistentes()

    # El metodo se define publico ya que ademas de ser usado dentro de __capacidadActual
    # y los metodos mostrar, tambien sera utilizado para realizar comparaciones entre eventos
    def cantidadAsistentes(self):
        return int(len(self.__asistentes))

#    # Método para eliminar un asistente del evento
    def eliminarAsistente(self, idValor, firebase, tipo):
        if idValor in self.__asistentes:
            # Antes se debe eliminar de la bd
            # tipo puede ser Fiestas, Conciertos, Matchs
            # Se elimina el dni de los asistentes del evento
            firebase.eliminarID(tipo, self.getID(), "asistentes", idValor)
            # Se elimina el id del evento de la lista de los eventos Asistidos
            firebase.eliminarID("Usuarios", idValor, "listaEventosAsistidos", self.getID())
            # Se elimina de la lista de eventos asistidos del objeto
            self.__asistentes.remove(idValor)
    #Datos generales
    def mostrarLista(self):
        return f"{self.__nombre}$&${self.__fecha}$&${self.__fechaFin}$&${self.__precio}$&${self.__capacidad}$&${self.__capacidadActual()}$&${self.cantidadAsistentes()}$&${self.__rango}"
        
    # Método para mostrar la lista de asistentes del evento con información de usuarios 
    def mostrarAsistentes(self, usuarios):
        cadenaAsistentes = "Asistentes\n"
        for asistente in self.__asistentes:
            for usuario in usuarios:
                if asistente==usuario.getDNI():
                    cadenaAsistentes += f"{usuario.mostrar()}\n"
                    break
    #Datos especificos
    def mostrar(self):
        return f"Nombre: {self.__nombre}\nFecha: {self.__fecha}\nFecha fin: {self.__fechaFin}\nPrecio: ${self.__precio}\nCapacidad: {self.__capacidad}\nCapacidad actual: {self.__capacidadActual()}\nCantidad de asistentes: {self.cantidadAsistentes()}\nRango: {self.__rango}"

    # Método para convertir el objeto Evento en un diccionario
    def objetoToDiccionario(self):
        # Se convierte en una lista para poder usarla luego cuando se deba crear otra vez el evento
        ubicacion = [self.__ubicacion.getLatitud(), self.__ubicacion.getLongitud(), self.__ubicacion.getDescripcion()]
        # El dni no se guarda porque sera el child para guardar el diccio de las clases que heredan Persona
        diccioEvento = {'nombre':self.getNombre(), 'fecha':self.getFecha(), 'ubicacion':ubicacion, 'precio':self.getPrecio(), 'descripcion':self.getDescripcion(), 'anfitrion':self.getAnfitrion(), 'asistentes':self.getAsistentes(), 'fechaFin':self.getFechaFin(), 'capacidad':self.getCapacidad(), 'rango':self.getRango()}
        return diccioEvento
