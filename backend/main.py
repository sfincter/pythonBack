from flask import Flask, jsonify, send_from_directory
from flask_pymongo import PyMongo
from datetime import datetime
import os

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')

# MongoDB configuration
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
mongo = PyMongo(app)

# Serve React frontend
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/button_hit', methods=['POST'])
def handle_button():
    try:
        event_data = {
            "event": "user hit button",
            "timestamp": datetime.now().isoformat()
        }
        
        mongo.db.button_clicks.insert_one(event_data)
        return jsonify({"message": "Click saved!"}), 200
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))