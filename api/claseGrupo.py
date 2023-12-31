# Define una clase llamada Grupo
# Es una clase abstracta que sirve como base para las clases Banda y Equipo
# No se realiza instancia de la misma
class Grupo():
    # En el constructor se encuentra **kwargs 
    # Es el parámetro que nos permite crear objetos a partir de pasarle un diccionario con todos los valores de los atributos
    # Como la base de datos de Firebase guarda en formato diccionario, es una forma más sencilla de volver a crear los objetos
    def __init__(self, **kwargs):
        # Inicializa los atributos de la clase con valores proporcionados en kwargs
        self.__id = kwargs.get('id', "") # Obtiene el valor del ID, o una cadena vacía si no se proporciona
        self.__nombre = kwargs.get('nombre') # Obtiene el valor del nombre
        self.__integrantes = kwargs.get('integrantes', []) # Obtiene la lista de integrantes o una lista vacía si no se proporciona


    # Getter para obtener el ID del grupo
    def getID(self):
        return self.__id
        
    # Getter para obtener el nombre del grupo
    def getNombre(self):
        return self.__nombre
        
    # Getter para obtener la lista de integrantes del grupo
    def getIntegrantes(self):
        return self.__integrantes

    # Setter para establecer el ID del grupo
    def setID(self, valor):
        self.__id = valor
        
    # Los siguientes setters seran utilizados por las clase hijas de Grupo, donde se le pasaran directamente el tipo especifico
    # Unicamente pueden actualizarse mediante su propio ID
    # Setter para establecer el nombre del grupo y actualizar en Firebase
    def setNombre(self, valor, firebase, tipo):
        if(firebase.editarAtributos(tipo, self.getID(), {'nombre': valor})):
            self.__nombre = valor

    # Setter para establecer un integrante en el grupo y actualizar en Firebase
    def setIntegrante(self, valor, firebase, tipo):
        diccioIntegrante = valor.objetoToDiccionario()
        if(firebase.editarAtributos(tipo, self.getID(), {'integrantes': diccioIntegrante}, "lista")):
            self.__integrantes.append(valor)

    # Método privado para mostrar la lista de integrantes en formato de cadena
    def __mostrarIntegrantes(self):
        datosInt = "Integrantes\n"
        for integrante in self.__integrantes:
            datosInt += f"{integrante.mostrar()}\n"
        return datosInt
        
    # Método para mostrar la información del grupo en formato de cadena
    def mostrarLista(self):
        return f"Nombre:{self.__nombre}\t"

    # Método para mostrar información detallada del grupo, incluyendo los integrantes
    def mostrar(self):
        return f"Nombre: {self.__nombre}\n{self.__mostrarIntegrantes()}"
