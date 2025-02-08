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

@app.route('/add', methods=['POST'])
def add_data():
    # Код для обработки данных
    try:
        data = request.json  # Получаем данные из запроса
        # Действия для добавления данных в базу данных
        mongo.db.myCollection.insert_one(data)
        return jsonify({"message": "Data added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        # Пробуем получить доступ к коллекции
        db = mongo.cx['myDatabase']  # Проверка подключения
        if db is None:
            return jsonify({"error": "MongoDB connection not established"}), 500

        # Если подключение успешно, возвращаем сообщение
        return jsonify({"message": "MongoDB connection successful!"}), 200

    except Exception as e:
        return jsonify({"error": f"Connection failed: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)