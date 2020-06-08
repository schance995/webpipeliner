from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app
from app.forms import LoginForm
import paramiko
from app.user import User

user = User()
ip = 'grace.umd.edu'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

@app.route('/')
@app.route('/index')
def index():
    if user.auth: # check for login
        return render_template('index.html', title='Home', user=user)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if user.auth:
        print('why is auth true?')
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit(): # is everything filled in correctly?
        username = form.username.data
        password = form.password.data
        try:
            ssh.connect(ip, username=username, password=password)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            user.name = username
            user.auth = True
            return redirect(next_page)
        except paramiko.AuthenticationException:
            flash('Invalid username or password')
            return redirect(url_for('login'))
        except Exception as e:
            print(e)
            flash('Something went wrong when logging in. Please try again.')
            return redirect(url_for('login'))
    return render_template('login.html',  title='Log In', form=form, user=user)

@app.route('/logout')
def logout():
    stdin,stdout,stderr=ssh.exec_command("ls")
    outlines = stdout.readlines()
    resp = ''.join(outlines)
    print(outlines)
    ssh.close() # logout
    user.auth = False
    return redirect(url_for('login'))
