from flask import Flask, render_template, jsonify
from flask_cors import CORS
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    current_date = datetime.now().strftime("%d.%m.%Y")
    return render_template('index.html', current_date=current_date)

@app.route('/api/message', methods=['GET'])
def get_message():
    return jsonify({'message': 'Привет от Flask!'})

if __name__ == '__main__':
    app.run(debug=True)