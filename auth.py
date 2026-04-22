import hashlib


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def registrar_usuario(conexion, nombre, correo, contrasena):
    try:
        conexion.rollback()  # Limpia cualquier transacción atorada
        cursor = conexion.cursor()
        cursor.execute('SELECT * FROM "user" WHERE user_email = %s', (correo,))
        if cursor.fetchone():
            return False, "Ese correo ya está registrado."

        pwd_hash = hash_password(contrasena)
        cursor.execute(
            'INSERT INTO "user" (user_name, user_email, password) VALUES (%s, %s, %s)',
            (nombre, correo, pwd_hash)
        )
        conexion.commit()
        cursor.close()
        return True, "Cuenta creada exitosamente."
    except Exception as e:
        conexion.rollback()
        return False, f"Error al registrar en la BD: {e}"


def iniciar_sesion(conexion, correo, contrasena):
    try:
        conexion.rollback()  # Limpia cualquier transacción atorada
        cursor = conexion.cursor()
        pwd_hash = hash_password(contrasena)
        cursor.execute(
            'SELECT user_id FROM "user" WHERE user_email = %s AND password = %s',
            (correo, pwd_hash)
        )
        usuario = cursor.fetchone()
        conexion.commit()  # Cierra la lectura exitosamente
        cursor.close()

        if usuario:
            return True, usuario[0]
        else:
            return False, "Correo o contraseña incorrectos."
    except Exception as e:
        conexion.rollback()
        return False, f"Error al consultar la BD: {e}"
