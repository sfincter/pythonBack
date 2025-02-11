from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import logging
import json


app = Flask(__name__)

# Подключение к базе данных
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель для данных
from sqlalchemy.dialects.mysql import JSON  # Для хранения массива данных в MySQL

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(120), nullable=False)
    salary = db.Column(db.Integer, nullable=True, default=0)
    options = db.Column(JSON)
    services = db.Column(db.Text, nullable=True, default="")  # JSON-строка
    service_type = db.Column(db.String(120))  # Тип консультации
    service_duration = db.Column(db.Integer)  # Длительность консультации
    service_price = db.Column(db.Integer)  # Стоимость консультации


# Создаем таблицы (если их нет)
with app.app_context():
    db.create_all()

import logging

logging.basicConfig(level=logging.DEBUG)


# Главная страница с формой
@app.route("/", methods=["GET", "POST"])
def index():
    try:
        if request.method == "POST":
            # Получаем данные из формы и добавляем их в базу
            data_input = request.form.get("data")
            salary_input = request.form.get("salary")
            has_salary = request.form.get("has_salary")  # Чекбокс "Получает оклад"
            service_type = request.form.get("service_type")
            service_duration = request.form.get("service_duration")
            service_price = request.form.get("service_price")
            options_input = request.form.getlist("options")

            # Обработка поля зарплаты
            if has_salary:  # Если чекбокс нажат
                try:
                    salary_value = int(salary_input) if salary_input else 0
                except ValueError:
                    return "Ошибка: Оклад должен быть числом", 400
            else:  # Если чекбокс НЕ нажат
                salary_value = None  # Или None, если нужно игнорировать поле



            salary_value = int(salary_input)
            duration_value = int(service_duration)
            price_value = int(service_price)

            new_data = Data(
                data=data_input,
                salary=salary_value,
                service_type=service_type,
                service_duration=duration_value,
                service_price=price_value,
                options=json.dumps(options_input)
            )

            db.session.add(new_data)
            db.session.commit()
            return redirect(url_for("index"))

        # Получаем все данные из БД
        all_data = Data.query.all()

        # Преобразуем JSON-строки обратно в списки для отображения
        for item in all_data:
            item.options = json.loads(item.options)

        return render_template("index.html", data=all_data)

    except Exception as e:
        logging.exception("Ошибка на сервере")
        return f"Ошибка сервера: {str(e)}", 500




    
@app.route("/delete/<int:data_id>", methods=["POST"])
def delete_data(data_id):
    try:
        data_to_delete = Data.query.get(data_id)
        if data_to_delete:
            db.session.delete(data_to_delete)
            db.session.commit()
    except Exception as e:
        print(f"Ошибка при удалении: {e}")
    
    return redirect(url_for("index"))



@app.route("/edit/<int:data_id>", methods=["GET", "POST"])
def edit_data(data_id):
    try:
        data_item = Data.query.get_or_404(data_id)

        if request.method == "POST":
            # Получаем данные из формы
            data_input = request.form["data"]
            salary_input = request.form["salary"]
            service_type = request.form.get("service_type")
            service_duration = request.form.get("service_duration")
            service_price = request.form.get("service_price")
            options_input = request.form.getlist("options")  # Получаем список выбранных чекбоксов

            # Обновляем запись в базе данных
            data_item.data = data_input
            data_item.salary = int(salary_input)
            data_item.service_type = service_type
            data_item.service_duration = int(service_duration)
            data_item.service_price = int(service_price)

            # Сохраняем выбранные специализации в формате JSON
            data_item.options = json.dumps(options_input)

            # Сохраняем изменения в базе данных
            db.session.commit()

            return redirect(url_for("index"))  # После успешного обновления, перенаправляем на главную страницу

        # Если метод GET, то показываем текущие данные
        return render_template("edit.html", data_item=data_item)

    except Exception as e:
        logging.exception("Ошибка при редактировании данных")
        return f"Ошибка сервера: {str(e)}", 500



if __name__ == '__main__':
    app.run(debug=True)
    app.config["PROPAGATE_EXCEPTIONS"] = True