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
            if "delete_all" in request.form:  # Если нажата кнопка "Удалить все записи"
                db.session.query(Data).delete()
                db.session.commit()
                return redirect(url_for("index"))

            data_input = request.form.get("data")
            salary_input = request.form.get("salary", "0")  # Если пустое - 0
            service_type = request.form.get("service_type")
            service_duration = request.form.get("service_duration", "0")
            service_price = request.form.get("service_price", "0")
            options = request.form.getlist("options")  # Получаем чекбоксы

            # Проверяем, включен ли чекбокс "Получает оклад"
            receives_salary = request.form.get("receives_salary")  # on или None
            salary_value = int(salary_input) if receives_salary else 0

            try:
                duration_value = int(service_duration)
                price_value = int(service_price)
            except ValueError:
                return "Ошибка: Длительность, зарплата и цена должны быть числами", 400

            new_data = Data(
                data=data_input,
                salary=salary_value,
                options=json.dumps(options),
                services=json.dumps([]),
                service_type=service_type,
                service_duration=duration_value,
                service_price=price_value
            )

            db.session.add(new_data)
            db.session.commit()
            return redirect(url_for("index"))

        # Получаем параметры сортировки
        order = request.args.get("order", "asc")  

        # Выборка данных с сортировкой
        if order == "asc":
            all_data = Data.query.order_by(Data.salary.asc()).all()
        else:
            all_data = Data.query.order_by(Data.salary.desc()).all()

        # Преобразуем JSON-строки обратно в списки
        for item in all_data:
            item.options = json.loads(item.options) if item.options else []
            item.services = json.loads(item.services) if item.services else []

        total_entries = Data.query.count()  # Подсчет общего количества записей

        return render_template("index.html", data=all_data, order=order, total_entries=total_entries)

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

            # Если чекбоксы не выбраны, присваиваем пустой список
            options_input = request.form.getlist("options") or []

            # Обновляем запись в базе данных
            data_item.data = data_input
            data_item.salary = int(salary_input) if salary_input else 0
            data_item.service_type = service_type
            data_item.service_duration = int(service_duration) if service_duration else 0
            data_item.service_price = int(service_price) if service_price else 0

            # Сохраняем выбранные специализации в формате JSON
            data_item.options = json.dumps(options_input)

            # Сохраняем изменения в базе данных
            db.session.commit()

            return redirect(url_for("index"))  # Перенаправляем на главную страницу

        # Десериализуем JSON обратно в список для корректного отображения чекбоксов
        data_item.options = json.loads(data_item.options) if data_item.options else []

        return render_template("edit.html", data_item=data_item)

    except Exception as e:
        logging.exception("Ошибка при редактировании данных")
        return f"Ошибка сервера: {str(e)}", 500




if __name__ == '__main__':
    app.run(debug=True)
    app.config["PROPAGATE_EXCEPTIONS"] = True