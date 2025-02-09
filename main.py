from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)

# Проверка подключения
@app.route('/')
def index():
    try:
        db.session.execute('SELECT 1')
        return "Connected to MySQL on Railway!"
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    app.run(debug=True)