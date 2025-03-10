from sqlite_manager import DatabaseManager
from flask import Flask

app = Flask(__name__)


# TODO: Crear una función que vigile un directorio y ejecute una acción cuando se detecte un cambio
def watch_folder():
    pass


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


if __name__ == "__main__":
    app.run()

    # Crear una instancia del gestor de base de datos
    db_manager = DatabaseManager("data/ejemplo.db")
    
    # Conectar a la base de datos
    if db_manager.connect():
        # Crear una tabla
        columns = {
            "id": "INTEGER PRIMARY KEY",
            "nombre": "TEXT NOT NULL",
            "edad": "INTEGER",
            "email": "TEXT UNIQUE"
        }
        db_manager.create_table("usuarios", columns)
        
        # Insertar datos
        usuario = {
            "nombre": "Juan Pérez",
            "edad": 30,
            "email": "juan@ejemplo.com"
        }
        usuario_id = db_manager.insert_data("usuarios", usuario)
        print(f"Usuario insertado con ID: {usuario_id}")
        
        # Consultar datos
        resultados = db_manager.execute_select("SELECT * FROM usuarios")
        print("Usuarios en la base de datos:")
        for usuario in resultados:
            print(usuario)
        
        # Actualizar datos
        actualizacion = {
            "edad": 31,
            "email": "juan.perez@ejemplo.com"
        }
        filas_actualizadas = db_manager.update_data("usuarios", actualizacion, "id = ?", (usuario_id,))
        print(f"Filas actualizadas: {filas_actualizadas}")
        
        # Consultar datos actualizados
        resultados = db_manager.execute_select("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
        print("Datos actualizados:")
        for usuario in resultados:
            print(usuario)
        
        # Eliminar datos
        # filas_eliminadas = db_manager.delete_data("usuarios", "id = ?", (usuario_id,))
        # print(f"Filas eliminadas: {filas_eliminadas}")
        
        # Desconectar de la base de datos
        db_manager.disconnect()
