class User:
    def __init__(self, usuario, password, rol):
        self.__usuario = usuario
        self.__password = password
        self.__rol = password
        
    def get_usuario(self):
        return self.__usuario
    
    def get_password(self):
        return self.__password
    
    def get_rol(self):
        return self.__rol