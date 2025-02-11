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
from sqlalchemy.dialects.mysql import JSON  # Для хранения массива данных в MySQL

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(120), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    options = db.Column(db.String(255), nullable=True, default="")
    services = db.Column(JSON, nullable=True, default=[])  # Храним список услуг


# Создаем таблицы (если их нет)
with app.app_context():
    db.create_all()

# Главная страница с формой
@app.route("/", methods=["GET", "POST"])
def index():
    search_query = request.args.get("search", "").strip()

    if request.method == "POST":
        data_input = request.form.get("data")
        salary_input = request.form.get("salary")
        options_input = request.form.getlist("options")
        service_type = request.form.get("service_type")
        service_duration = request.form.get("service_duration")
        service_price = request.form.get("service_price")

        if data_input and salary_input:
            try:
                salary_value = int(salary_input)
                options_value = ", ".join(options_input) if options_input else ""

                # Формируем объект услуги
                service = {
                    "type": service_type,
                    "duration": service_duration,
                    "price": service_price
                }

                # Получаем старые услуги и добавляем новую
                existing_services = []
                if request.form.get("existing_services"):
                    existing_services = json.loads(request.form.get("existing_services"))
                
                existing_services.append(service)

                new_data = Data(
                    data=data_input,
                    salary=salary_value,
                    options=options_value,
                    services=existing_services  # Сохраняем массив услуг
                )

                db.session.add(new_data)
                db.session.commit()
                return redirect(url_for("index"))
            except ValueError:
                return "Ошибка: зарплата и цена должны быть числами", 400

    # Фильтрация поиска
    if search_query:
        all_data = Data.query.filter(
            (Data.data.ilike(f"%{search_query}%")) | 
            (Data.salary == search_query) | 
            (Data.options.ilike(f"%{search_query}%")) | 
            (Data.services.ilike(f"%{search_query}%"))
        ).all()
    else:
        all_data = Data.query.all()

    return render_template("index.html", data=all_data, search_query=search_query)




    
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