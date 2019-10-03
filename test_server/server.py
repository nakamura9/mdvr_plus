from flask import Flask
from flask import jsonify

app = Flask(__name__)

@app.route('/StandardApiAction_login.action')
def login():
    return jsonify({
        'result': 0,
        'jsession': '3u1239uuijjr8ew7324'
    })


@app.route('/StandardApiAction_queryTrackDetail.action')
def get_tracks():
    return jsonify({
        'result': 0
    })

if __name__ == "__main__":
    app.run(debug=True)