import bcrypt
def create_password(pw):
    return bcrypt.hashpw(pw, bcrypt.gensalt())

def verify_password(user, pw):
    return bcrypt.hashpw(pw.encode(), user.password.encode()) == user.password.encode()
