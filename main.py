from controllers.watchdog_controller import WatchdogsController
from controllers.sqlite_controller import DatabaseController
from controllers.prefect_controller import proccess_query
from flask import Flask, request, jsonify

app = Flask(__name__)


# TODO: GET the web page
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


# post /watchdog that receives the query parameters path and action
@app.route("/query", methods=["POST"])
def query():
    if request.json is not None:
        query = request.json.get("query")
        if query:
            proccess_query(query)
    else:
        return jsonify({"error": "Invalid JSON body"}), 400

    return jsonify({"status": "ok"})


def database_init(db_manager: DatabaseController):
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


if __name__ == "__main__":
    # Iniciar la vigilancia en segundo plano
    watcher = WatchdogsController("./filesystem")
    watcher.start()

    # Iniciar la base de datos y crear la estructura
    db_manager = DatabaseController("data/database.db")
    database_init(db_manager)

    # Iniciar backend de Flask
    app.run(debug=True, port=5000, host="0.0.0.0")
