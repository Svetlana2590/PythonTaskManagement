from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from models import TMSDB


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, email):
        user = TMSDB.User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже используется')

    def validate_username(self, username):
        user = TMSDB.User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Это имя пользователя уже используется')


class TaskForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    description = TextAreaField('Описание')
    status = SelectField('Статус', choices=[
            ('Not started', 'Не начата'),
            ('In progress', 'В процессе'),
            ('Completed', 'Выполнена')
        ], validators=[DataRequired()])
    submit = SubmitField('Сохранить')