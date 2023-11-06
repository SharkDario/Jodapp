
class Persona():
    def __init__(self, **kwargs):
        self.__dni = kwargs.get('dni')
        self.__nombre = kwargs.get('nombre')
        self.__apellido = kwargs.get('apellido')
        self.__edad = kwargs.get('edad')

    #def __init__(self, dni, nombre, apellido, edad):
    #    self.__dni = dni
    #    self.__nombre = nombre
    #    self.__apellido = apellido
    #    self.__edad = edad

    def getDNI(self):
        return self.__dni
    
    def getNombre(self):
        return self.__nombre
    
    def getApellido(self):
        return self.__apellido
    
    def getEdad(self):
        return self.__edad
    
    def setDNI(self, valor, firebase, tipo):
        # Si se cambio en la bd quiere decir que era un dni distinto a uno existente, y devuelve True
        if(firebase.editarID(tipo, self.getDNI(), valor)):
            self.__dni = valor

    def setNombre(self, valor, firebase, tipo):
        # Si se cambio en la bd quiere decir que era un nombre distinto a uno existente, y devuelve True
        if(firebase.editarAtributos(tipo, self.getDNI(), {'nombre': valor})):
            self.__nombre = valor

    def setApellido(self, valor, firebase, tipo):
        if(firebase.editarAtributos(tipo, self.getDNI(), {'apellido': valor})):
            self.__apellido = valor

    def setEdad(self, valor, firebase, tipo):
        if(firebase.editarAtributos(tipo, self.getDNI(), {'edad': valor})):
            self.__edad =valor

    def mostrar(self):
        return f"DNI: {self.__dni}\nNombre: {self.__nombre}\nApellido: {self.__apellido}\nEdad: {self.__edad}\n"
    
    def objetoToDiccionario(self):
        # El dni no se guarda porque sera el child para guardar el diccio de las clases que heredan Persona
        diccioPersona = {'nombre':self.getNombre(), 'apellido':self.getApellido(), 'edad':self.getEdad()}
        return diccioPersona