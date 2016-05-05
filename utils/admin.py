import bcrypt
import oath
def create_password(pw):
    return bcrypt.hashpw(pw, bcrypt.gensalt())

def verify_password(user, pw):
    return bcrypt.hashpw(pw.encode(), user.password.encode()) == user.password.encode()

def verify_otp(user, otp):
    return oath.from_b32key(user.secret).accept(otp)
