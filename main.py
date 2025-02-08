from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)

# Настройка MongoDB
app.config["MONGO_URI"] = "mongodb+srv://samyrize77777:6A8zrE9ULIInxEHR@cluster0.ahmvu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # замените на вашу строку подключения
mongo = PyMongo(app)

@app.route('/', methods=['GET'])
def get_response():
    return jsonify({"status": "OK"})

# Пример роута для добавления данных в MongoDB
@app.route('/add', methods=['POST'])
def add_data():
    data = request.json  # Получаем JSON-данные из запроса
    mongo.db.myCollection.insert_one(data)  # Вставляем данные в коллекцию
    return jsonify({"message": "Data added successfully!"}), 201

@app.route('/data', methods=['GET'])
def get_data():
    try:
        data = mongo.db.myCollection.find()  # Находим все документы в коллекции
        result = []

        for item in data:
            # Преобразуем _id в строку для корректного отображения в JSON
            item['_id'] = str(item['_id'])  
            result.append(item)

        return jsonify(result), 200

    except Exception as e:
        # Если возникает ошибка, возвращаем описание ошибки
        return jsonify({"error": str(e)}), 500
    

@app.route('/test', methods=['GET'])
def test_db():
    try:
        # Пример простого запроса к коллекции для проверки
        mongo.db.myCollection.count_documents({})
        return jsonify({"message": "Connection to MongoDB successful!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)