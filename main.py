from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)

# Настройка MongoDB
app.config["MONGO_URI"] = "mongodb+srv://samyrize77777:6A8zrE9ULIInxEHR@cluster0.ahmvu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # замените на вашу строку подключения
mongo = PyMongo(app)

# Пример роута для добавления данных в MongoDB
@app.route('/add', methods=['POST'])
def add_data():
    data = request.json  # Получаем JSON-данные из запроса
    mongo.db.myCollection.insert_one(data)  # Вставляем данные в коллекцию
    return jsonify({"message": "Data added successfully!"}), 201

# Пример роута для получения данных из MongoDB
@app.route('/data', methods=['GET'])
def get_data():
    data = mongo.db.myCollection.find()  # Находим все документы в коллекции
    result = []
    for item in data:
        item['_id'] = str(item['_id'])  # Преобразуем _id в строку для JSON
        result.append(item)
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)