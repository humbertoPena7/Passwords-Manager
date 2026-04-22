import os
import hashlib
import base64
import random
import string
import re
from cryptography.fernet import Fernet


class VaultManager:
    WORD_LIST = [
        "gato", "sol", "montana", "rio", "nube", "libro", "ventana", "camino", "puente", "sombra",
        "fuego", "viento", "tierra", "mar", "hoja", "piedra", "luz", "noche", "dia", "estrella",
        "bosque", "nieve", "arena", "cristal", "hierro", "cielo", "valle", "isla", "tiempo", "reloj",
        "espacio", "viaje", "musica", "arte", "ciencia", "teoria", "cosmos", "planeta", "atomo", "energia"
    ]

    def __init__(self, db_connection, user_id, master_password):
        self.conn = db_connection
        self.user_id = user_id
        self.vault_data = []

        key = hashlib.sha256(master_password.encode()).digest()
        self.cipher_suite = Fernet(base64.urlsafe_b64encode(key))
        self.load_from_db()

    def load_from_db(self):
        try:
            self.conn.rollback()  # Limpiar estado
            cursor = self.conn.cursor()
            query = "SELECT password_id, website, email, password FROM password WHERE user_id = %s"
            cursor.execute(query, (self.user_id,))
            rows = cursor.fetchall()

            self.vault_data = []
            for r in rows:
                self.vault_data.append({
                    'id': r[0],
                    'site': r[1],
                    'username': r[2],
                    'password': r[3]
                })
            self.conn.commit()
            cursor.close()
        except Exception as e:
            self.conn.rollback()
            print(f"Error cargando datos: {e}")

    def add_record(self, site, username, password):
        try:
            self.conn.rollback()
            enc_p = self.cipher_suite.encrypt(password.encode()).decode()
            cursor = self.conn.cursor()
            query = "INSERT INTO password (user_id, website, email, password) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (self.user_id, site, username, enc_p))
            self.conn.commit()
            cursor.close()
            self.load_from_db()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error al guardar: {e}")
            return False

    def update_record(self, rid, site, username, password):
        try:
            self.conn.rollback()
            enc_p = self.cipher_suite.encrypt(password.encode()).decode()
            cursor = self.conn.cursor()
            query = "UPDATE password SET website=%s, email=%s, password=%s WHERE password_id=%s AND user_id=%s"
            cursor.execute(query, (site, username, enc_p, rid, self.user_id))
            self.conn.commit()
            cursor.close()
            self.load_from_db()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error al actualizar: {e}")
            return False

    def delete_record(self, rid):
        try:
            self.conn.rollback()
            cursor = self.conn.cursor()
            query = "DELETE FROM password WHERE password_id=%s AND user_id=%s"
            cursor.execute(query, (rid, self.user_id))
            self.conn.commit()
            cursor.close()
            self.load_from_db()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error al eliminar: {e}")
            return False

    def decrypt(self, encrypted_password):
        try:
            if isinstance(encrypted_password, str):
                encrypted_password = encrypted_password.encode()
            return self.cipher_suite.decrypt(encrypted_password).decode()
        except:
            return "Error al desencriptar"

    @staticmethod
    def check_strength(password):
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
