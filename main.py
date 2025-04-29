from controllers.watchdog_controller import WatchdogsController
from controllers.sqlite_controller import DatabaseController
from controllers.llm_studio_controller import LMStudioController
from controllers.prefect_controller import proccess_query

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

from controllers.chroma_controller import ChromaClient

app = Flask(
    __name__,
    static_folder="./llm-search-front/dist",
    template_folder="./llm-search-front/dist"
)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:*"}})

# Load ChromaDB client
chroma_db = ChromaClient("./data/chroma_db")

# Create or retrieve the ChromaDB collection
chroma_db.create_chroma_collection(collection_name="llm_search_collection")

@app.route("/")
def web_page():
    return render_template("index.html")

@app.route("/assets/<path:path>")
def serve_assets(path):
    return send_from_directory("./llm-search-front/dist/assets", path)

@app.route("/favicon.ico")
def favicon():
    return send_from_directory("./llm-search-front/dist", "favicon.ico")

# TODO: Modificar el contolador de ChromaDB para que devuelva los datos requeridos
@app.route("/api/status", methods=["GET"])
def get_status():
    # Get total processed files in the ChromaDB database
    total_processed_files = DatabaseController.get_total_files()
    # Get total files in the filesystem
    total_files = WatchdogsController.get_total_files()
    # Get total in process files in the filesystem
    total_in_process_files = WatchdogsController.get_total_in_process_files()
    # Get total of each file type in the database
    total_files_by_type = DatabaseController.get_total_files_by_type()
    # Get encountered errors
    encountered_errors = WatchdogsController.get_encountered_errors()

    return jsonify({
        "total_processed_files": total_processed_files,
        "total_files": total_files,
        "total_in_process_files": total_in_process_files,
        "total_files_by_type": total_files_by_type,
        "encountered_errors": encountered_errors
    })


@app.route("/api/models", methods=["GET"])
def get_models():
    return jsonify(LMStudioController.get_models())

@app.route("/api/query", methods=["POST"])
def query():
    if request.json is not None:
        query = request.json.get("query")
        model = request.json.get("model")
        temperature = request.json.get("temperature", 0.7)
        verbose = request.json.get("verbose", False)
        if query:
            result = proccess_query(query, model, temperature, verbose)
            return jsonify({"result": str(result)})
    return jsonify({"message": "Invalid JSON body"}), 400


@app.route("/api/path_descs", methods=["GET"])
def get_db_descs():
    return chroma_db.get_all_paths()


@app.route("/api/path_descs", methods=["POST"])
def get_db_desc_by_path():
    if request.json is not None:
        result = chroma_db.get_desc_with_path(request.json["path"])
        if result:
            return jsonify(result)
        else:
            return jsonify({"message": "No results found"}), 404
    return jsonify({"message": "Invalid JSON body"}), 400
    


if __name__ == "__main__":
    # Initialize logging
    watcher = WatchdogsController("./filesystem")
    watcher.start()

    # Initialize Database Controller
    # db_manager = DatabaseController("data/database.db")

    # Initialize Flask app backend
    app.run(debug=False, port=5000, host="0.0.0.0")
