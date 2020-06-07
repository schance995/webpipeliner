from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm
from app.user import User

user = User()

@app.route('/')
@app.route('/index')
def index():
    if user.auth:
        return render_template('index.html', title='Home', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if user.auth:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user.auth = True
        user.name = form.username.data
        flash('Login requested for user {}, password={}'.format(
            form.username.data, form.password.data))
        return redirect(url_for('index'))
    return render_template('login.html',  title='Sign In', form=form)

@app.route('/logout')
def logout():
    user.auth = False
    return redirect(url_for('login'))
