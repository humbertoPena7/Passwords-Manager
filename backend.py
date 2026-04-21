import os
import hashlib
import base64
import random
import string
import re
from cryptography.fernet import Fernet


class VaultManager:
    """Gestiona el almacenamiento en memoria y la criptografía de la app."""

    WORD_LIST = [
        "gato", "sol", "montana", "rio", "nube", "libro", "ventana", "camino", "puente", "sombra",
        "fuego", "viento", "tierra", "mar", "hoja", "piedra", "luz", "noche", "dia", "estrella",
        "bosque", "nieve", "arena", "cristal", "hierro", "cielo", "valle", "isla", "tiempo", "reloj",
        "espacio", "viaje", "musica", "arte", "ciencia", "teoria", "cosmos", "planeta", "atomo", "energia"
    ]

    def __init__(self):
        self.master_hash = None
        self.salt = None
        self.cipher_suite = None
        self.vault_data = []
        self.next_id = 1

    # --- AUTENTICACIÓN Y CIFRADO ---
    def authenticate(self, password):
        """Valida el login o registra la clave maestra si es la primera vez."""
        if self.master_hash is None:
            self.salt = os.urandom(16)
            self.master_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), self.salt, 100000)
            fernet_key = base64.urlsafe_b64encode(hashlib.pbkdf2_hmac('sha256', password.encode(), self.salt, 100000))
            self.cipher_suite = Fernet(fernet_key)
            return True
        else:
            test_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), self.salt, 100000)
            return test_hash == self.master_hash

    def decrypt(self, encrypted_password):
        return self.cipher_suite.decrypt(encrypted_password).decode()

    # --- GESTIÓN DE DATOS (CRUD) ---
    def add_record(self, site, username, password):
        enc_p = self.cipher_suite.encrypt(password.encode())
        self.vault_data.append({'id': self.next_id, 'site': site, 'username': username, 'password': enc_p})
        self.next_id += 1

    def update_record(self, rid, site, username, password):
        enc_p = self.cipher_suite.encrypt(password.encode())
        for r in self.vault_data:
            if r['id'] == rid:
                r.update({'site': site, 'username': username, 'password': enc_p})
                break

    def delete_record(self, rid):
        self.vault_data = [r for r in self.vault_data if r['id'] != rid]

    # --- REGLAS DE NEGOCIO (NIST Y GENERADOR) ---
    @staticmethod
    def check_strength(password):
        """Evalúa seguridad según NIST (Prioriza longitud)."""
        length = len(password)
        if length == 0: return 0, "gray", "Vacía"
        if length < 8: return 0.2, "#E74C3C", "Muy Corta"

        score = 0.4
        if length >= 12: score += 0.2
        if length >= 16: score += 0.2
        if length >= 20: score += 0.1

        if re.search(r"[A-Z]", password) and re.search(r"[a-z]", password): score += 0.05
        if re.search(r"\d", password): score += 0.05
        if re.search(r"[^A-Za-z0-9]", password): score += 0.05

        score = min(score, 1.0)
        if score < 0.5: return score, "#E74C3C", "Débil"
        if score < 0.7: return score, "#F1C40F", "Aceptable"
        if score < 0.9: return score, "#2ECC71", "Fuerte"
        return score, "#1ABC9C", "Óptima"

    @classmethod
    def generate_password(cls, mode, length, upper, lower, nums, syms):
        """Generador universal (Caracteres o Frase)"""
        if mode == "Caracteres":
            chars = ""
            if upper: chars += string.ascii_uppercase
            if lower: chars += string.ascii_lowercase
            if nums: chars += string.digits
            if syms: chars += "!@#$%^&*()_+=-{}[]|:;<>,.?"
            if not chars: return ""
            return "".join(random.choice(chars) for _ in range(length))
        else:
            words = random.choices(cls.WORD_LIST, k=length)
            words[-1] += str(random.randint(0, 9))
            return "-".join(words)
