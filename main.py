from flask import Flask, render_template, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Разрешаем кросс-доменные запросы

# Настройка подключения к MongoDB
app.config["MONGO_URI"] = "mongodb+srv://samyrize77777:6A8zrE9ULIInxEHR@cluster0.ahmvu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/button_hit', methods=['POST'])
def handle_button():
    try:
        # Создаем запись для базы данных
        event_data = {
            "event": "user hit button",
            "timestamp": datetime.now()
        }
        
        # Вставляем данные в коллекцию
        mongo.db.button_clicks.insert_one(event_data)
        
        return jsonify({"message": "Button click saved successfully!"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/data')
def show_data():
    try:
        clicks = list(mongo.db.button_clicks.find({}, {'_id': 0}))
        return jsonify(clicks), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)