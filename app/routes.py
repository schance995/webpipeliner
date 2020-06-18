from flask import render_template, flash, redirect, url_for, request, jsonify
from werkzeug.urls import url_parse
from app import app
from app.forms import LoginForm, BasicsForm
import paramiko
from app.user import User
from app.families import getFamilies, getGenomes, getPipelines, FAMILIES_JSON

user = User()
'''
ip = 'grace.umd.edu' # for testing
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
'''

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', current_user=user), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html', current_user=user), 500

@app.route('/')
@app.route('/step1', methods=['GET', 'POST'])
def step1():
    if not user.auth: # check for login
        return redirect(url_for('login'))
        
    form = BasicsForm()
    # was everything filled in correctly
    if form.validate_on_submit():
        flash('You clicked the submit button.')
        return redirect(url_for('step1'))
    return render_template('step1.html', title='Step 1', current_user=user, form=form, families=FAMILIES_JSON)

'''
@app.route('/dynamic/<family>') # takes a pipeline parameter
def dynamic(family):
    return jsonify(familiesAsDict())
'''
'''
pipelineArray = []
for p in pipelines:
    pipelineObj = {}
    pipelineObj['pipeline'] = p
    pipelineArray.append(pipelineObj)
return jsonify({'pipelines': pipelineArray})
'''
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
        # disabled ssh login for now.
        user.name = username
        user.auth = True
        flash('Login successful')
        return redirect(url_for('step1'))
        '''
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
        '''
    return render_template('login.html',  title='Log In', form=form, current_user=user)

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
