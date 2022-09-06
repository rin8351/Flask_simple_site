from flask import Blueprint, render_template, url_for, redirect, session, request, flash, g
from models import db, User

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

menu = [
        {'url': '.listusers', 'title': 'Список пользователей'},
        {'url': '.logout', 'title': 'Выйти'}
        ]

def isLogged():
    return True if session.get('admin_logged') else False

def login_admin():
    session['admin_logged'] = 1

def logout_admin():
    session.pop('admin_logged', None)

@admin.route('/')
def index():
    if not isLogged():
        return redirect(url_for('.login'))

    return render_template('admin/index.html', menu=menu, title='Админ-панель')

@admin.route('/login', methods=["POST", "GET"])
def login():
    if isLogged():
        return redirect(url_for('.index'))

    if request.method == "POST":
        if request.form['user'] == "admin" and request.form['psw'] == "12345":
            login_admin()
            return redirect(url_for('.index'))
        else:
            flash("Неверная пара логин/пароль", "error")

    return render_template('admin/login.html', title='Админ-панель')


@admin.route('/logout', methods=["POST", "GET"])
def logout():
    if not isLogged():
        return redirect(url_for('.index'))

    logout_admin()

    return redirect(url_for('index'))

@admin.route('/list-users')
def listusers():
    if not isLogged():
        return redirect(url_for('.login'))

    users = []
    # Получаем список пользователей из БД
    for user in db.session.query(User).all():
        users.append(user)
    return render_template('admin/listusers.html', title='Список пользователей', menu=menu, users=users)