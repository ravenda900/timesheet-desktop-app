import os
import json
from cryptography.fernet import Fernet

# Encryption class for storing and retrieving credentials
class EncryptionManager:
    def __init__(self, key_file="secret.key"):
        self.key_file = key_file
        self.key = self.load_or_generate_key()
        self.cipher_suite = Fernet(self.key)

    def load_or_generate_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as key_file:
                key_file.write(key)
            return key

    def encrypt_data(self, data):
        return self.cipher_suite.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data):
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()

    def store_credentials(self, email, password):
        credentials = {"email": email, "password": password}
        encrypted_email = self.encrypt_data(credentials["email"])
        encrypted_password = self.encrypt_data(credentials["password"])
        with open("credentials.json", "w") as file:
            json.dump({"email": encrypted_email, "password": encrypted_password}, file)

    def load_credentials(self):
        if os.path.exists("credentials.json"):
            with open("credentials.json", "r") as file:
                encrypted_data = json.load(file)
                email = self.decrypt_data(encrypted_data["email"])
                password = self.decrypt_data(encrypted_data["password"])
                return email, password
        return None, None

    def remove_credentials(self):
        if os.path.exists("credentials.json"):
            os.remove("credentials.json")