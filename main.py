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
    options = db.Column(db.String(255), nullable=True, default="")
    services = db.Column(db.Text, nullable=True, default="")  # JSON-строка


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
            data_input = request.form.get("data")
            salary_input = request.form.get("salary")
            service_type = request.form.get("service_type")
            service_duration = request.form.get("service_duration")
            service_price = request.form.get("service_price")

            # Получаем все выбранные чекбоксы
            selected_options = request.form.getlist("options")  # список значений чекбоксов
            options_json = json.dumps(selected_options)  # Преобразуем в JSON-строку

            # Проверка на заполненные поля
            if not data_input or not salary_input:
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

            # Преобразуем список в JSON-строку
            services_json = json.dumps(existing_services)

            # Создание новой записи
            new_data = Data(
                data=data_input,
                salary=salary_value,
                services=services_json,
                options=options_json  # Сохраняем выбранные чекбоксы
            )

            db.session.add(new_data)
            db.session.commit()
            return redirect(url_for("index"))

        # Получаем все данные из БД
        all_data = Data.query.all()

        # Преобразуем JSON-строки обратно в списки словарей
        for item in all_data:
            if isinstance(item.services, str):
                try:
                    item.services = json.loads(item.services)
                except json.JSONDecodeError:
                    item.services = []  # Если парсинг не удался, делаем пустым списком

            if isinstance(item.options, str):
                try:
                    item.options = json.loads(item.options)  # Преобразуем JSON в список
                except json.JSONDecodeError:
                    item.options = []  # Если ошибка, делаем пустым списком

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
    # Получаем данные записи по ID или возвращаем 404, если запись не найдена
    data_item = Data.query.get(data_id)

    if not data_item:
        # Если запись не найдена, возвращаем ошибку 404
        return "Запись не найдена", 404

    if request.method == "POST":
        # Обновляем данные из формы
        data_item.data = request.form['data']
        data_item.salary = request.form['salary']
        data_item.options = " , ".join(request.form.getlist('options'))  # Обновляем выбранные опции

        # Сохраняем изменения в базе данных
        db.session.commit()
        return redirect(url_for("index"))  # Перенаправляем на главную страницу

    # Если GET-запрос, то заполняем форму данными для редактирования
    return render_template("edit.html", data_item=data_item)



if __name__ == '__main__':
    app.run(debug=True)
    app.config["PROPAGATE_EXCEPTIONS"] = True