from flask import Flask, render_template
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Подключение к базе данных
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Главная страница
@app.route('/')
def index():
    try:
        # Пытаемся выполнить запрос к базе данных
        result = db.session.execute('SELECT 1')
        return "Database is connected!"
    except Exception as e:
        # Если ошибка, выводим её
        return f"Error: {str(e)}"

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
