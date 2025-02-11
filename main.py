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
    salary = db.Column(db.Integer, nullable=False)
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


# Главная страница с формой и сортировкой
@app.route("/", methods=["GET", "POST"])
def index():
    try:
        if request.method == "POST":
            data_input = request.form.get("data")
            salary_input = request.form.get("salary")
            service_type = request.form.get("service_type")
            service_duration = request.form.get("service_duration")
            service_price = request.form.get("service_price")
            options = request.form.getlist("options")  # Чек-боксы

            # Проверка на заполненные поля
            if not data_input or not salary_input or not service_duration or not service_price:
                return "Ошибка: Заполните все поля", 400

            try:
                salary_value = int(salary_input)
                duration_value = int(service_duration)
                price_value = int(service_price)
            except ValueError:
                return "Ошибка: Длительность, зарплата и цена должны быть числами", 400

            # Загружаем существующие услуги (если есть)
            existing_services = []
            if request.form.get("existing_services"):
                existing_services = json.loads(request.form.get("existing_services"))

            # Добавляем новую услугу
            new_service = {
                "type": service_type,
                "duration": duration_value,
                "price": price_value
            }
            existing_services.append(new_service)

            # Преобразуем список в JSON
            services_json = json.dumps(existing_services)
            options_json = json.dumps(options)

            # Создание новой записи
            new_data = Data(
                data=data_input,
                salary=salary_value,
                services=services_json,
                options=options_json
            )

            db.session.add(new_data)
            db.session.commit()
            return redirect(url_for("index"))

        # Получаем параметры сортировки
        order = request.args.get("order", "asc")  

        # Выборка данных с сортировкой
        if order == "asc":
            all_data = Data.query.order_by(Data.salary.asc()).all()
        elif order == "desc":
            all_data = Data.query.order_by(Data.salary.desc()).all()
        else:
            all_data = Data.query.all()

        # Преобразуем JSON-строки обратно в списки словарей
        for item in all_data:
            item.services = json.loads(item.services) if item.services else []
            item.options = json.loads(item.options) if item.options else []

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
        # Загружаем запись из базы данных
        data_item = Data.query.get_or_404(data_id)

        if request.method == "POST":
            # Получаем данные из формы
            data_item.data = request.form['data']
            data_item.salary = request.form['salary']
            data_item.service_type = request.form['service_type']
            data_item.service_duration = request.form['service_duration']
            data_item.service_price = request.form['service_price']

            # Проверка на положительные числа для зарплаты и стоимости
            try:
                salary_value = float(data_item.salary)
                price_value = float(data_item.service_price)

                if salary_value <= 0 or price_value <= 0:
                    return "Ошибка: Зарплата и стоимость должны быть положительными числами", 400
            except ValueError:
                return "Ошибка: Зарплата и стоимость должны быть числами", 400

            # Обработка специализаций (чекбоксы)
            selected_options = request.form.getlist('options')  # Получаем список выбранных чекбоксов
            data_item.options = json.dumps(selected_options)  # Преобразуем в JSON

            # Сохраняем изменения в базе данных
            db.session.commit()

            return redirect(url_for('index'))  # Перенаправляем на главную страницу

        # Если метод GET, то просто передаем данные для редактирования
        data_item.options = json.loads(data_item.options) if data_item.options else []
        return render_template('edit.html', data_item=data_item)

    except Exception as e:
        logging.exception("Ошибка при редактировании данных")
        return f"Ошибка сервера: {str(e)}", 500


if __name__ == '__main__':
    app.run(debug=True)
    app.config["PROPAGATE_EXCEPTIONS"] = True