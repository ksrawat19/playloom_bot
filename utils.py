# optional

import hashlib

SECRET_KEY = "secret-key123"

def generate_token(url: str) -> str:
    return hashlib.md5(f"{url}{SECRET_KEY}".encode()).hexdigest()

def validate_token(url: str, token: str) -> bool:
    return generate_token(url) == token
