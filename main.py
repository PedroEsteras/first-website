
from datetime import date
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, PasswordField
from wtforms.validators import DataRequired, EqualTo, NumberRange, Email, Length, ValidationError
from flask_sqlalchemy import SQLAlchemy

# --------------------- Create App and Database ---------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfCU792donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tables.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --------------------- Create Database Table ---------------------


class Users(db.Model):
    id = db.Column(db.Integer, autoincrement=True)
    username = db.Column(db.String, unique=True, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    mail = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    age = db.Column(db.Integer, nullable=False)


db.create_all()

# --------------------- Year and Age ---------------------
birth_date = date(2003, 11, 14)
today = date.today()
year = today.year
time_difference = today - birth_date
age = (time_difference.days/365.2425).__floor__()


# --------------------- Routes ---------------------
# ---- Home ----
@app.route("/")
def home():
    return render_template("index.html", year=year, age=age)

# ---- Log In ----
def login_check(form, field):
    users_passwords = {user.username: user.password for user in db.session.query(Users).all()}
    users = [user.username for user in db.session.query(Users).all()]

    if not form.username.data in users:
        raise ValidationError('El usuario o la contraseña son incorrectos.')
    if not field.data == users_passwords[form.username.data]:
        raise ValidationError('El usuario o la contraseña son incorrectos.')

class LogInForm(FlaskForm):
    username = StringField(label="Usuario", validators=[
                           DataRequired(message="Este campo es obligatorio")])
    password = PasswordField(label="Contraseña", validators=[
                             DataRequired(message="Este campo es obligatorio"), login_check])
    submit = SubmitField(label="Ingresar")


@app.route("/ingresar", methods=["GET", "POST"])
def log_in():
    form = LogInForm()
    if form.validate_on_submit():
        return redirect(url_for('main', username=form.username.data))
    return render_template("login.html", form=form, year=year)

# ---- Register ----
def taken_username_check(user, field):
    users = [user.username for user in db.session.query(Users).all() ]
    if field.data in users:
        raise ValidationError('El nombre de usuario ya esta utilizado')

class RegisterForm(FlaskForm):
    name = StringField(label="Nombre y apellido", validators=[
                       DataRequired(message="Este campo es obligatorio")])
    age = IntegerField(label="Edad", validators=[DataRequired(message="Este campo es obligatorio"), NumberRange(
        min=16, message="Debes tener al menos 16 años para registrarte"), NumberRange(max=110, message="Introduzca una edad valida")])
    mail = StringField(label="Mail", validators=[DataRequired(
        message="Este campo es obligatorio"), Email(message="Mail invalido")])
    username = StringField(label="Nombre de usuario", validators=[DataRequired(message="Este campo es obligatorio"), Length(
        min=6, message="El nombre de usuario debe tener al menos 6 caracteres."), taken_username_check])
    password = PasswordField(label="Contraseña", validators=[DataRequired(message="Este campo es obligatorio"), Length(
        min=6, message="La contraseña debe tener al menos 6 caracteres.")])
    confirm_password = PasswordField(label="Confirmar contraseña", validators=[
                                     DataRequired(message="Este campo es obligatorio"), EqualTo('password', message="Las contraseñas no coinciden")])
    submit = SubmitField(label="Registrarme")


@app.route("/registrarme", methods=["GET", "POST"])
def register():
    global verification_number
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = Users(id=1, username=form.username.data, name=form.name.data,
                         mail=form.mail.data, password=form.password.data, age=form.age.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main', username=form.username.data))
    return render_template("register.html", form=form, year=year)

# ---- Main ----
@app.route("/main", methods=["GET", "POST"])
def main():
    username = request.args.get("username")
    return render_template("main.html", year=year)


# --------------------- Run App ---------------------
if __name__ == "__main__":
    app.run(debug=True)
