from flask import Flask, render_template, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Настройка подключения к MongoDB
app.config["MONGO_URI"] = "mongodb+srv://samyrize77777:6A8zrE9ULIInxEHR@cluster0.ahmvu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/button_hit', methods=['POST'])
def handle_button():
    try:
        print("Attempting to connect to DB...")  # Логируем начало операции
        
        event_data = {
            "event": "user hit button",
            "timestamp": datetime.now().isoformat()
        }
        
        # Логируем данные перед вставкой
        print(f"Inserting data: {event_data}")
        
        result = mongo.db.button_clicks.insert_one(event_data)
        print(f"Insert result ID: {result.inserted_id}")  # Логируем ID документа
        
        return jsonify({"message": "Click saved!"}), 200
    
    except Exception as e:
        print(f"!!! CRITICAL ERROR: {str(e)}")  # Подробное логирование ошибки
        return jsonify({"error": "Database operation failed"}), 500

@app.route('/data')
def show_data():
    try:
        clicks = list(mongo.db.button_clicks.find({}, {'_id': 0}))
        return jsonify(clicks), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)