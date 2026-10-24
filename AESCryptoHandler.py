from cryptography.fernet import Fernet

class AESCryptoHandler:
    def __init__(self, key: bytes = None):
        self.key = key if key else Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def encrypt(self, data: bytes) -> bytes:
        return self.cipher.encrypt(data)

    def decrypt(self, encrypted_data: bytes) -> bytes:
        return self.cipher.decrypt(encrypted_data)

    def get_key(self) -> bytes:
        return self.key