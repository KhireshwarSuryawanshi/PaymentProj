from werkzeug.security import generate_password_hash,check_password_hash

class User:
    def __init__(self, username,phonum,email,password,deposit):
        self.username = username
        self.phonum = phonum
        self.email = email
        self._password_hash= None
        self.set_password(password)
        self.deposit = deposit

    def set_password ( self, password):
        if len(password) < 6:
            raise ValueError("password must be more tahn 6 char long")
        self._password_hash = password

    def get_password(self):
        return self._password_hash
    
    def check_password(self, password):
        return check_password_hash(self._password_hash,password)

    