from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Подключение к базе данных
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель для данных
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(120), nullable=False)

# Создаем таблицы (если их нет)
with app.app_context():
    db.create_all()

# Главная страница с формой
@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
            data_input = request.form['data']
            new_data = Data(data=data_input)
            db.session.add(new_data)
            db.session.commit()
            return redirect(url_for('index'))
        
        all_data = Data.query.all()
        return render_template('index.html', data=all_data)
    
    except Exception as e:
        logging.exception("Ошибка при обработке запроса")
        return f"Ошибка сервера: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
    app.config["PROPAGATE_EXCEPTIONS"] = True
