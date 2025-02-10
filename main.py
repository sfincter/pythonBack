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
    salary = db.Column(db.Integer, nullable=False)
    options = db.Column(db.Text, nullable=True)

# Создаем таблицы (если их нет)
with app.app_context():
    db.create_all()

# Главная страница с формой
@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
            data_input = request.form['data']
            salary_input = request.form.get('salary', 0)
            
            # Получаем массив выбранных опций
            selected_options = request.form.getlist('options')  # ['Option 1', 'Option 2']
            options_str = ",".join(selected_options)  # Преобразуем в строку: "Option 1,Option 2"

            new_data = Data(data=data_input, salary=int(salary_input), options=options_str)
            db.session.add(new_data)
            db.session.commit()
            return redirect(url_for('index'))
        
        all_data = Data.query.all()
        return render_template('index.html', data=all_data)
    
    except Exception as e:
        logging.exception("Ошибка при обработке запроса")
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
    # Получаем данные записи по ID
    data_item = Data.query.get_or_404(data_id)

    if request.method == "POST":
        # Обновляем данные
        data_item.data = request.form['data']
        data_item.salary = request.form['salary']
        data_item.options = ",".join(request.form.getlist('options'))  # Обновляем выбранные опции

        # Сохраняем изменения в базе данных
        db.session.commit()
        return redirect(url_for("index"))  # Перенаправляем на главную страницу

    # Если GET-запрос, то заполняем форму данными для редактирования
    return render_template("edit.html", data_item=data_item)


if __name__ == '__main__':
    app.run(debug=True)
    app.config["PROPAGATE_EXCEPTIONS"] = True