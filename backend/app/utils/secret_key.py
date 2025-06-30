import secrets

def generate_secret_key(length: int = 32) -> str:
    return secrets.token_urlsafe(length)

if __name__ == "__main__":
    print(generate_secret_key())
