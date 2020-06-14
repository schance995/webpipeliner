from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app
from app.forms import LoginForm, BasicsForm
import paramiko
from app.user import User
from app.determinators import getFamilies, getGenomes, getPipelines

user = User()
ip = 'grace.umd.edu' # for testing
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

@app.route('/')
@app.route('/step1', methods=['GET', 'POST'])
def step1():
    if not user.auth: # check for login
        return redirect(url_for('login'))
        
    form = BasicsForm()
    form.pipeline.choices = [(p.lower(), p) for p in getPipelines('ExomeSeq')] # tmp default choices put in the correct dynamic choices later.
    form.genome.choices = [(g.lower(), g) for g in getGenomes('ExomeSeq')] # tmp default choices for now
    if form.validate_on_submit():
        flash('You clicked the submit button.')
        return redirect(url_for('step1'))
    return render_template('step1.html', title='Step 1', user=user, form=form)

@app.route('/dynamic/<family>') # takes a pipeline parameter
def dynamic(family):
    pipelines = getPipelines(family) # get the family's pipelines
    pipelineArray = []
    for p in pipelines:
        pipelineObj = {}
        pipelineObj['pipeline'] = p
        pipelineArray.append(pipelineObj)
    return jsonify({'pipelines': pipelineArray})
# will be interpreted as an object in javascript
# this route is called every time the state changes

@app.route('/login', methods=['GET', 'POST'])
def login():
    if user.auth:
        return redirect(url_for('step1'))
    form = LoginForm()
    if form.validate_on_submit(): # is everything filled in correctly?
        username = form.username.data
        password = form.password.data
        try: # to login
            # will configure ssh later
            # ssh.connect(ip, username=username, password=password)
            user.name = username
            user.auth = True
            flash('Login successful')
            return redirect(url_for('step1'))
        except paramiko.AuthenticationException: # wrong credentials
            flash('Invalid username or password')
            return redirect(url_for('login'))
        except Exception as e: # some other error
            print(e)
            flash('Something went wrong when logging in. Please try again.')
            return redirect(url_for('login'))
    return render_template('login.html',  title='Log In', form=form, user=user)

@app.route('/logout')
def logout():
    '''
    stdin,stdout,stderr=ssh.exec_command("ls")
    outlines = stdout.readlines()
    resp = ''.join(outlines)
    print(outlines)
    sh.close() # logout
    '''
    user.auth = False
    return redirect(url_for('login'))
