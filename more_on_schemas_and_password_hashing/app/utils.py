from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # for the password hashing


def hash(password):
    return pwd_context.hash(password)