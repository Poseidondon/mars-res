from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_restful import Api
from wtforms import StringField, PasswordField, SubmitField, IntegerField, BooleanField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from flask_ngrok import run_with_ngrok

from data import db_session
from data.__all_models import *
from users_resources import UserResource, UsersListResource
from jobs_resources import JobsResource, JobsListResource

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
run_with_ngrok(app)

api = Api(app)
api.add_resource(UsersListResource, '/api/v2/users')
api.add_resource(UserResource, '/api/v2/users/<int:user_id>')
api.add_resource(JobsListResource, '/api/v2/jobs')
api.add_resource(JobsResource, '/api/v2/jobs/<int:job_id>')

login_manager = LoginManager()
login_manager.init_app(app)


class AddJobForm(FlaskForm):
    title = TextAreaField("Описание работы", validators=[DataRequired()])
    duration = IntegerField("Продолжительность", validators=[DataRequired()])
    collaborators = StringField("ID соучастников (через ', ')")
    is_finished = BooleanField("Выполнено")
    submit = SubmitField()

    def __init__(self, btn_text='Add'):
        super(AddJobForm, self).__init__()
        self.submit.label.text = btn_text


class RegisterForm(FlaskForm):
    email = EmailField('Login / email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat password', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    speciality = StringField('Speciality', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/')
def jobs():
    session = db_session.create_session()
    jobs_list = session.query(Jobs)
    return render_template('jobs.html', title='Работы', jobs=jobs_list)


@app.route('/job',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = AddJobForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        job = Jobs()
        job.job = form.title.data
        current_user.jobs.append(job)
        job.work_size = form.duration.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('add_job.html', title='Добавление работы',
                           form=form)


@app.route('/job_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    session = db_session.create_session()
    job = session.query(Jobs).filter((Jobs.id == id) & ((Jobs.user == current_user) | (id == 1))).first()
    if job:
        session.delete(job)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/job/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = AddJobForm('Edit')
    if request.method == "GET":
        session = db_session.create_session()
        job = session.query(Jobs).filter((Jobs.id == id) & ((Jobs.user == current_user) | (id == 1))).first()
        if job:
            form.title.data = job.job
            form.duration.data = job.work_size
            form.collaborators.data = job.collaborators
            form.is_finished.data = job.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        job = session.query(Jobs).filter((Jobs.id == id) & ((Jobs.user == current_user) | (id == 1))).first()

        if job:
            job.job = form.title.data
            job.work_size = form.duration.data
            job.collaborators = form.collaborators.data
            job.is_finished = form.is_finished.data
            session.commit()
            return redirect('/')
        else:
            abort(418)
    return render_template('add_job.html', title='Редактирование новости', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            email=form.email.data,
            age=form.age.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


def main():
    db_session.global_init("db/blogs.sqlite")

    ses = db_session.create_session()
    ses.query(Jobs).filter(Jobs.id >= 4).delete()
    ses.commit()

    app.run()


if __name__ == '__main__':
    main()
