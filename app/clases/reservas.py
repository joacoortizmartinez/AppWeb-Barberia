class Reserva:
    def __init__(self, nombre, telefono, sucursal, fecha, hora):
        self.__nombre = nombre
        self.__telefono = telefono
        self.__sucursal = sucursal
        self.__fecha = fecha
        self.__hora = hora
        
    def get_nombre(self):
        return self.__nombre
    
    def get_telefono(self):
        return self.__telefono
    
    def get_sucursal(self):
        return self.__sucursal
    
    def get_fecha(self):
        return self.__fecha
    
    def get_hora(self):
        return self.__hora