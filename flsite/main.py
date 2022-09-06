from flask import Flask, render_template, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import LoginForm, RegisterForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,SelectField,SubmitField,TextAreaField
from admin.admin import admin
from models import User, db,app

app.register_blueprint(admin, url_prefix='/admin')

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category',
        backref=db.backref('posts', lazy='dynamic'))
    pub_date = db.Column(db.DateTime)

    def __init__(self, title, body, category, pub_date=None):
        self.title = title
        self.body = body
        self.category = category
        self.pub_date = datetime.utcnow()

    def __repr__(self):
        return '<Post %r>' % self.title

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % self.name

class PostForm(FlaskForm):
    title = StringField('Заголовок поста')
    body = TextAreaField('Текст поста', render_kw={'rows': 10, 'cols': 30})
    category = SelectField('Категория', coerce=int)
    submit = SubmitField('Добавить')


@app.route('/')
def index():
    return render_template('index.html', posts=Post.query.all())

@app.route('/addpost', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    form.category.choices = [(category.id, category.name) for category in Category.query.all()]
    if form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data, category=Category.query.get(form.category.data))
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('addpost.html', form=form)

@app.route('/post/<int:post_id>')
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not check_password_hash(user.psw, form.psw.data):
            flash('Неверный логин или пароль')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.name.data, email=form.email.data)
        user.psw = generate_password_hash(form.psw.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html',title="Профиль")


    
if __name__ == "__main__":
    app.run(debug=True)

#db.create_all()
