from flask import render_template, url_for, flash, redirect,request
from articles import app,db,bcrypt
from articles.forms import RegistrationForm, LoginForm,ArticleForm
from articles.models import User, Article
from flask_login import login_user, current_user, logout_user, login_required
import os
import secrets

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def home():
    articles = Article.query.all()
    return render_template('home.html', articles=articles)

@app.route("/my_articles")
@login_required
def my_articles():
    # # return 'current_user'
    my_articles = Article.query.filter_by(user_id =current_user.id).all()
    return render_template('my_articles.html', title=my_articles, my_articles=my_articles)
    # return render_template('my_articles.html')


@app.route("/my_articles/new", methods=['GET', 'POST'])
@login_required
def new():
    form = ArticleForm()
    if form.validate_on_submit():
        article = Article(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(article)
        db.session.commit()
        flash('Your article has been created!', 'success')
        return redirect(url_for('my_articles'))
    return render_template('new.html', title='New article',
                           form=form, legend='New article')


@app.route("/my_articles/<int:article_id>/update", methods=['GET', 'POST'])
@login_required
def update(article_id):
    article = Article.query.get_or_404(article_id)
    form = ArticleForm()
    if form.validate_on_submit():
        article.title = form.title.data
        article.content = form.content.data
        db.session.commit()
        flash('Your article has been updated!', 'success')
        return redirect(url_for('article', article_id=article.id))
    elif request.method == 'GET':
        form.title.data = article.title
        form.content.data = article.content
    return render_template('new.html', title='Update article',
                           form=form, legend='Update article')


@app.route("/my_articles/<int:article_id>/delete", methods=['POST'])
@login_required
def delete(article_id):
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    flash('Your article has been deleted!', 'success')
    return redirect(url_for('home'))
    
