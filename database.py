import psycopg2
from tkinter import messagebox

# Funcion para la conexion a PostgreSQL
def database_connection():
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="passwords",
            user="postgres",
            password="789123"
        )
        return connection

    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos.\n{e}")
        return None
      
