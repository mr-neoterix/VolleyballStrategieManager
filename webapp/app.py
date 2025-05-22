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


@app.route('/api/formations', methods=['GET', 'POST'])
def formations():
    """List or append formations."""
    if request.method == 'POST':
        formation = request.get_json(silent=True)
        if not formation:
            return jsonify({'error': 'Invalid data'}), 400
        formations = load_json(FORMATIONS_PATH)
        formations.append(formation)
        save_json(FORMATIONS_PATH, formations)
        return jsonify({'status': 'ok'})
    return jsonify(load_json(FORMATIONS_PATH))


@app.route('/api/formations/<int:idx>', methods=['PUT', 'DELETE'])
def formations_modify(idx):
    """Update or delete a formation by index."""
    formations = load_json(FORMATIONS_PATH)
    if idx < 0 or idx >= len(formations):
        return jsonify({'error': 'invalid index'}), 404
    if request.method == 'DELETE':
        formations.pop(idx)
    else:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Invalid data'}), 400
        formations[idx] = data
    save_json(FORMATIONS_PATH, formations)
    return jsonify({'status': 'ok'})


@app.route('/api/teams', methods=['GET', 'POST'])
def teams():
    """List or append teams."""
    if request.method == 'POST':
        team = request.get_json(silent=True)
        if not team:
            return jsonify({'error': 'Invalid data'}), 400
        teams = load_json(TEAMS_PATH)
        teams.append(team)
        save_json(TEAMS_PATH, teams)
        return jsonify({'status': 'ok'})
    return jsonify(load_json(TEAMS_PATH))


@app.route('/api/teams/<int:idx>', methods=['DELETE'])
def teams_delete(idx):
    teams = load_json(TEAMS_PATH)
    if idx < 0 or idx >= len(teams):
        return jsonify({'error': 'invalid index'}), 404
    teams.pop(idx)
    save_json(TEAMS_PATH, teams)
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
