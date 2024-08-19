class User:
    def __init__(self, usuario, password):
        self.__usuario = usuario
        self.__password = password
        
    def get_usuario(self):
        return self.__usuario
    
    def get_password(self):
        return self.__password