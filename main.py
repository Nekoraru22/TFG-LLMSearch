import os

from controllers.watchdog_controller import WatchdogsController
from controllers.sqlite_controller import DatabaseController
from controllers.lm_studio_controller import LMStudioController
from controllers.prefect_controller import proccess_query

from flask import Flask, request, jsonify, render_template, send_from_directory, send_file
from flask_cors import CORS

from controllers.chroma_controller import ChromaClient, create_graphics

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = Flask(
    __name__,
    static_folder="./llm-search-front/dist",
    template_folder="./llm-search-front/dist"
)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:*"}})

# Load ChromaDB client
chroma_db = ChromaClient(str(os.environ.get("CHROMA_DB_PATH")))

# Create or retrieve the ChromaDB collection
chroma_db.create_chroma_collection(collection_name=str(os.environ.get("CHROMA_COLLECTION_NAME")))


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

@app.route('/api/file_content', methods=['GET'])
def file_content():
    path = request.args.get('path')
    if not path:
        return jsonify({"error": "No path provided"}), 400
    
    # Security check to prevent directory traversal
    if '..' in path:
        return jsonify({"error": "Invalid path"}), 400
    
    try:
        # Check if file exists
        if not os.path.exists(path):
            return jsonify({"error": "File not found"}), 404
            
        # For images, return the file contents
        return send_file(path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/file_details", methods=["POST"])
def get_db_desc_by_path():
    if request.json is not None:
        result = chroma_db.get_desc_with_path(request.json["path"])
        if result:
            return jsonify(result)
        else:
            return jsonify({"message": "No results found"}), 404
    return jsonify({"message": "Invalid JSON body"}), 400
    

if __name__ == "__main__":
    create_graphics("two characters with cat ears and tail", True)
    exit(0)
    # Initialize logging
    watcher = WatchdogsController(str(os.environ.get("TRACKED_FOLDER")))
    watcher.start()

    # Initialize Database Controller
    # db_manager = DatabaseController("data/database.db")

    # Initialize Flask app backend
    app.run(debug=False, port=5000, host="0.0.0.0")
