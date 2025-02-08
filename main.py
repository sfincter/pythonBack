import requests
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)

# Настройка подключения к MongoDB
app.config["MONGO_URI"] = "mongodb+srv://samyrize77777:6A8zrE9ULIInxEHR@cluster0.ahmvu.mongodb.net/myDatabase?retryWrites=true&w=majority"
mongo = PyMongo(app)

# Маршрут для добавления данных
@app.route('/add', methods=['POST'])
def add_data():
    try:
        data = request.json  # Получаем данные из запроса
        if data is None:  # Проверяем, что данные пришли
            return jsonify({"error": "No data received"}), 400

        # Вставляем данные в коллекцию MongoDB
        mongo.db.myCollection.insert_one(data)

        # Отправляем тестовые данные на другой маршрут с использованием requests
        test_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30
        }

        response = requests.post('https://pythonback-production-fbdb.up.railway.app/test', json=test_data)  # Отправляем данные на /test

        if response.status_code == 200:
            print("Test data successfully sent:", response.json())
        else:
            print("Failed to send test data:", response.status_code)

        return jsonify({"message": "Data added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Дополнительный маршрут для теста
@app.route('/test', methods=['POST'])
def test_route():
    try:
        test_data = request.json  # Получаем тестовые данные
        if test_data:
            return jsonify({"message": "Test data received", "data": test_data}), 200
        return jsonify({"error": "No data received"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
