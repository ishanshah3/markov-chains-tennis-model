from flask import Flask, request, jsonify, send_from_directory
import os

# Use the project's modeling and dataset code
try:
    from src.markov_modeling import compute_probabilities
    from src.dataset import df, player_stats
except ImportError:
    from markov_modeling import compute_probabilities
    from dataset import df, player_stats

APP_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, static_folder=APP_DIR)


@app.route('/')
def index():
    return send_from_directory(APP_DIR, 'index.html')


@app.route('/probabilities', methods=['POST'])
def probabilities():
    body = request.get_json() or {}
    p1 = body.get('player1')
    p2 = body.get('player2')
    surface = body.get('surface', 'Clay')

    if not p1 or not p2 or p1.strip().lower() == p2.strip().lower():
        return jsonify({'error': 'Provide two different player names.'}), 400

    # Use dataset.player_stats to extract serve/return from real data
    serve1, return1 = player_stats(df, p1, surface)
    serve2, return2 = player_stats(df, p2, surface)

    result = compute_probabilities(serve1, return1, serve2, return2)

    return jsonify(result)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8501))
    app.run(host='0.0.0.0', port=port, debug=True)
