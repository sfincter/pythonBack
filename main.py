from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Подключение к базе данных
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель для данных
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(120), nullable=False)

# Главная страница с формой
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data_input = request.form['data']

        # Добавление данных в базу данных
        new_data = Data(data=data_input)
        db.session.add(new_data)
        db.session.commit()

        # Перенаправление на главную страницу после добавления
        return redirect(url_for('index'))
    
    # Получаем все данные из базы для отображения
    all_data = Data.query.all()
    return render_template('index.html', data=all_data)

if __name__ == '__main__':
    app.run(debug=True)
