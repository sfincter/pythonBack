import os
from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Форматируем DATABASE_URL для SQLAlchemy (заменяем mysql:// на mysql+pymysql://)
DATABASE_URL = os.getenv("DATABASE_URL", "").replace("mysql+pymysql://root:DmRAFbxJAuoroDekTYiWQBiTMndpFcXr@junction.proxy.rlwy.net:32757/railway")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Определение модели данных
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(120), nullable=False)

# Создаем таблицы (если их нет)
with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data_input = request.form["data"]
        
        # Запись в базу
        new_data = Data(data=data_input)
        db.session.add(new_data)
        db.session.commit()

        return redirect(url_for("index"))

    # Получение всех записей из базы
    all_data = Data.query.all()
    return render_template("index.html", data=all_data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
