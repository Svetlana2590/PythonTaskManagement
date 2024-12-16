from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegistrationForm, TaskForm
from models import TMSDB, db


db = SQLAlchemy()


app = Flask(__name__) #создаём приложение
app.config['SECRET_KEY'] = 'taskmanagementsystemsecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5433/task_manager'  #адрес для подключения
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  #передаём приложение

with app.app_context():
    db.create_all()
    db.session.commit()

login_manager = LoginManager(app)
login_manager.login_view = 'login'



import psycopg2
from psycopg2 import Error

try:
    # Подключение к существующей базе данных
    connection = psycopg2.connect(user="postgres",
                                  # пароль, который указали при установке PostgreSQL
                                  password="QmtA7b",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="postgres_db")

    # Курсор для выполнения операций с базой данных
    cursor = connection.cursor()
    # Распечатать сведения о PostgreSQL
    print("Информация о сервере PostgreSQL")
    print(connection.get_dsn_parameters(), "\n")
    # Выполнение SQL-запроса
    cursor.execute("SELECT version();")
    # Получить результат
    record = cursor.fetchone()
    print("Вы подключены к - ", record, "\n")

except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL", error)
finally:
    if connection:
        cursor.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто")



@login_manager.user_loader
def load_user(user_id):
    return TMSDB.User.query.get(user_id)


@app.route('/') #создаем главную страницу
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = TMSDB.User.query.filter_by(email=form.email.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Неверный логин или пароль', 'danger')
        else:
            flash('Некорректно введены данные', 'danger')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            hashed_password = generate_password_hash(form.password.data)
            new_user = TMSDB.User(username=form.username.data,
                                  email=form.email.data,
                                  password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            flash('Некорректно введены данные', 'danger')
    return render_template('register.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    tasks = TMSDB.Task.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', tasks=tasks)


@app.route('/task/new', methods=['GET', 'POST'])
@login_required
def new_task():
    form = TaskForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            task = TMSDB.Task(title=form.title.data,
                              description=form.description.data,
                              status=form.status.data,
                              user_id=current_user.id)
            db.session.add(task)
            db.session.commit()
            flash('Задача создана', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Некорректно введены данные', 'danger')
    return render_template('task_form.html', form=form)


@app.route('/task/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = TMSDB.Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('У вас нет доступа к этой задаче', 'danger')
        return redirect(url_for('dashboard'))

    form = TaskForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            task.title = form.title.data
            task.description = form.description.data
            task.status = form.status.data
            db.session.commit()
            flash('Задача обновлена', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Некорректно введены данные', 'danger')
    form.title.data = task.title
    form.description.data = task.description
    form.status.data = task.status
    return render_template('task_form.html', form=form)


@app.route('/task/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = TMSDB.Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('У вас нет доступа к этой задаче', 'danger')
        return redirect(url_for('dashboard'))

    db.session.delete(task)
    db.session.commit()
    flash('Задача удалена', 'success')
    return redirect(url_for('dashboard'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')