import json, sys, os, importlib.util
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def import_scraper(site_name):
    file_path = f"resources/sites/{site_name}.py"
    if not os.path.exists(file_path):
        return None
    spec = importlib.util.spec_from_file_location(site_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[site_name] = module
    spec.loader.exec_module(module)
    return module

@app.route('/streams')
def get_streams():
    tmdb_id = request.args.get('id')
    media_type = request.args.get('type')
    season = request.args.get('s', 1, type=int)
    episode = request.args.get('e', 1, type=int)
    if not tmdb_id:
        return jsonify({"error": "Missing id"}), 400
    module = import_scraper('wiflix')
    if module and hasattr(module, 'getStreams'):
        try:
            streams = module.getStreams(tmdb_id, media_type, season, episode)
            return jsonify(streams)
        except Exception:
            return jsonify([])
    return jsonify([])

@app.route('/')
def index():
    return "vStream proxy ready"
