from app.models import User, Task
from app.forms import LoginForm, RegistrationForm, TaskForm
from urllib.parse import urlparse
from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_user, logout_user, login_required
import bleach

bp = Blueprint('main', __name__)

# Rutas principales
@bp.route('/')
@bp.route('/index')
@login_required
def index():
    tasks = Task.get_all_by_user(current_user.id)
    return render_template('index.html', title='Home', tasks=tasks)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=bleach.clean(form.username.data), email=bleach.clean(form.email.data))
        user.set_password(form.password.data)
        user.save()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

# Rutas para tareas
@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(description=bleach.clean(form.description.data), user_id=current_user.id)
        task.save()
        flash('Your task is now live!')
        return redirect(url_for('main.index'))
    return render_template('todo.html', title='Add Task', form=form)

@bp.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    task = Task.get(id)
    if task is None or task.user_id != current_user.id:
        abort(403)
    form = TaskForm()
    if form.validate_on_submit():
        task.description = bleach.clean(form.description.data)
        task.save()
        flash('Your task has been updated.')
        return redirect(url_for('main.index'))
    elif request.method == 'GET':
        form.description.data = task.description
    return render_template('todo.html', title='Edit Task', form=form)

@bp.route('/delete/<id>', methods=['POST'])
@login_required
def delete_task(id):
    task = Task.get(id)
    if task is None or task.user_id != current_user.id:
        abort(403)
    task.delete()
    flash('Your task has been deleted.')
    return redirect(url_for('main.index'))
