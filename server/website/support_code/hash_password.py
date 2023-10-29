import hashlib


def convert_password_to_hash(password: str):
    hash_password = hashlib.sha256()
    hash_password.update(password)
    return hash_password.hexdigest()
