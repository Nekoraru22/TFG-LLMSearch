from controllers.watchdog_controller import WatchdogsController
from controllers.sqlite_controller import DatabaseController
from controllers.prefect_controller import proccess_query
from controllers.llm_studio_controller import LLMStudioController
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

app = Flask(
    __name__,
    static_folder="./llm-search-front/dist",
    template_folder="./llm-search-front/dist"
)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:*"}})


@app.route("/")
def web_page():
    return render_template("index.html")

@app.route("/assets/<path:path>")
def serve_assets(path):
    return send_from_directory("./llm-search-front/dist/assets", path)

@app.route("/favicon.ico")
def favicon():
    return send_from_directory("./llm-search-front/dist", "favicon.ico")

@app.route("/api/models", methods=["GET"])
def get_models():
    return jsonify(LLMStudioController.get_models())

@app.route("/api/query", methods=["POST"])
def query():
    if request.json is not None:
        query = request.json.get("query")
        model = request.json.get("model")
        temperature = request.json.get("temperature", 0.7)
        if query:
            result = proccess_query(query, model, temperature)
            return jsonify({"result": str(result)})
    return jsonify({"message": "Invalid JSON body"}), 400


if __name__ == "__main__":
    # Initialize logging
    watcher = WatchdogsController("./filesystem")
    watcher.start()

    # Initialize Database Controller
    # db_manager = DatabaseController("data/database.db")

    # Initialize Flask app backend
    app.run(debug=False, port=5000, host="0.0.0.0")
