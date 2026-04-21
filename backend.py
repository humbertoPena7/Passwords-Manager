import os
import hashlib
import base64
import random
import string
import re
from cryptography.fernet import Fernet
from database import database_connection  # Importación de la BASE DE DATOS


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
        self.current_user_id = 1  # Fijo temporalmente para no tocar el login

    # --- AUTENTICACIÓN Y CIFRADO ---
    def authenticate(self, password):
        """Valida el login y carga los datos desde PostgreSQL."""
        if self.master_hash is None:

            self.salt = b'1234567890123456' #token de 16 bytes fijo (es temporal)

            self.master_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), self.salt, 100000)
            fernet_key = base64.urlsafe_b64encode(hashlib.pbkdf2_hmac('sha256', password.encode(), self.salt, 100000))
            self.cipher_suite = Fernet(fernet_key)
            self.load_data_from_db()  # Cargamos de la BD al entrar
            return True
        else:
            test_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), self.salt, 100000)
            if test_hash == self.master_hash:
                self.load_data_from_db()
                return True
            return False

    def decrypt(self, encrypted_password):
        # Fernet puede recibir strings o bytes
        if isinstance(encrypted_password, str):
            encrypted_password = encrypted_password.encode('utf-8')
        return self.cipher_suite.decrypt(encrypted_password).decode()

    # --- GESTIÓN DE DATOS (CRUD CON POSTGRESQL) ---
    def load_data_from_db(self):
        """Obtiene las contraseñas de la base de datos y las pone en memoria para la UI."""
        conn = database_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT password_id, website, email, password FROM password WHERE user_id = %s",
                    (self.current_user_id,)
                )
                records = cursor.fetchall()
                self.vault_data = []
                for row in records:
                    self.vault_data.append({
                        'id': row[0],
                        'site': row[1],
                        'username': row[2],
                        'password': row[3]  # Contraseña cifrada en la BD
                    })
            finally:
                cursor.close()
                conn.close()

    def add_record(self, site, username, password):
        # Ciframos y convertimos a string para guardar en VARCHAR(100)
        enc_p = self.cipher_suite.encrypt(password.encode()).decode('utf-8')

        conn = database_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO password (user_id, password, email, website)
                    VALUES (%s, %s, %s, %s) RETURNING password_id
                    """,
                    (self.current_user_id, enc_p, username, site)
                )
                new_id = cursor.fetchone()[0]
                conn.commit()
                # Actualizamos la memoria para que la UI lo vea al instante
                self.vault_data.append({'id': new_id, 'site': site, 'username': username, 'password': enc_p})
            finally:
                cursor.close()
                conn.close()

    def update_record(self, rid, site, username, password):
        enc_p = self.cipher_suite.encrypt(password.encode()).decode('utf-8')

        conn = database_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE password SET website = %s, email = %s, password = %s
                    WHERE password_id = %s AND user_id = %s
                    """,
                    (site, username, enc_p, rid, self.current_user_id)
                )
                conn.commit()
                # Actualizamos la memoria
                for r in self.vault_data:
                    if r['id'] == rid:
                        r.update({'site': site, 'username': username, 'password': enc_p})
                        break
            finally:
                cursor.close()
                conn.close()

    def delete_record(self, rid):
        conn = database_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM password WHERE password_id = %s AND user_id = %s",
                    (rid, self.current_user_id)
                )
                conn.commit()
                # Removemos de la memoria
                self.vault_data = [r for r in self.vault_data if r['id'] != rid]
            finally:
                cursor.close()
                conn.close()

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
