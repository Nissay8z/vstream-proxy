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

priority_sites = ['wiflix', 'dpstream', '1seriestreaming', 'voirfilms', 'zone_telechargement']

@app.route('/streams')
def get_streams():
    tmdb_id = request.args.get('id')
    media_type = request.args.get('type')
    season = request.args.get('s', 1, type=int)
    episode = request.args.get('e', 1, type=int)
    if not tmdb_id:
        return jsonify({"error": "Missing id"}), 400
    for site in priority_sites:
        module = import_scraper(site)
        if module and hasattr(module, 'getStreams'):
            try:
                streams = module.getStreams(tmdb_id, media_type, season, episode)
                if streams and len(streams) > 0:
                    return jsonify(streams)
            except Exception:
                continue
    return jsonify([])

@app.route('/')
def index():
    return "vStream proxy ready"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
