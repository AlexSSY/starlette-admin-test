from passlib.hash import pbkdf2_sha256


def hash_password(plain_password):
    return pbkdf2_sha256.hash(plain_password)


def check_password(plain_password, password_hash):
    return pbkdf2_sha256.verify(plain_password, password_hash)
