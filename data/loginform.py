from flask_wtf import FlaskForm
from wtforms.fields.simple import EmailField, PasswordField, BooleanField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Создать')
