import json
import os
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORMATIONS_PATH = os.path.join(BASE_DIR, 'formations.json')
TEAMS_PATH = os.path.join(BASE_DIR, 'teams.json')


def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as fh:
        return json.load(fh)


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/formations')
def get_formations():
    return jsonify(load_json(FORMATIONS_PATH))


@app.route('/api/teams')
def get_teams():
    return jsonify(load_json(TEAMS_PATH))


@app.route('/api/save_formation', methods=['POST'])
def save_formation():
    formation = request.get_json(silent=True)
    if not formation:
        return jsonify({'error': 'Invalid data'}), 400
    formations = load_json(FORMATIONS_PATH)
    formations.append(formation)
    save_json(FORMATIONS_PATH, formations)
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
