from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()

# Таблицы для базы данных
class TMSDB:
    class User(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String, nullable=False, unique=True)
        email = db.Column(db.String, nullable=False, unique=True)
        password = db.Column(db.String, nullable=False)

        tasks = db.relationship('Task', backref='user', lazy=True) #связывает таблицы


    class Task(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String, nullable=False)
        description = db.Column(db.Text)
        status = db.Column(db.String, nullable=False, default='Not started')
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    class Post(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(200), nullable=False)
        content = db.Column(db.Text, nullable=False)
        author_nickname = db.Column(db.String(100), nullable=False)  # Поле для никнейма автора
        comments = db.relationship('Comment', backref='post', lazy=True)

    class Comment(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        content = db.Column(db.Text, nullable=False)
        author_nickname = db.Column(db.String(100), nullable=False)  # Поле для никнейма автора
        post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)