import json
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, redirect, render_template
from datetime import datetime
from sqlalchemy import create_engine

# -------------------------
# 1. Leer configuración desde el JSON
# -------------------------
import json
import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import create_engine

# -------------------------
# 1. Leer configuración desde el JSON
# -------------------------
with open("C:/scripts/KLS_KOF_Crud_SQL_VER_0/Keys/Configsqlpl.json") as config_file:
    config = json.load(config_file)

username = config["username"]
password = config["password"]
server = config["server"]
database = config["database"]
table = config["table"]

# -------------------------
# 2. Configuración Flask + SQL Server
# -------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mssql+pyodbc://{username}:{password}@{server}/{database}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------------
# 3. Modelo de la tabla (igual que en SQL Server)
# -------------------------
class mytask(db.Model):
    __tablename__ = table  # Usa el nombre de la tabla del JSON
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.content}>'

# -------------------------
# 4. CRUD
# -------------------------

# ➤ CREATE + READ
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        current_task = request.form['content']
        new_task = mytask(content=current_task)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f"Error al guardar: {e}"
    else:
        tasks = mytask.query.order_by(mytask.created).all()
        return render_template('index.html', tasks=tasks)

# ➤ UPDATE (marcar como completa)
@app.route("/edit/<int:id>", methods=['POST', 'GET'])
def edit_task(id: int):
    task_to_edit = mytask.query.get_or_404(id)
    if request.method == 'POST':
        task_to_edit.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except Exception as e:
            print(f"Error: {e}")
            return f"Error: {e}"
    else:
        return render_template('edit.html', task=task_to_edit)

# ➤ DELETE
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = mytask.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f"Error al eliminar: {e}"

# -------------------------
# 5. Ejecutar la app
# -------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Crea la tabla si no existe
    app.run(debug=True)
