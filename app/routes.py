from flask import render_template, flash, redirect, url_for, request, jsonify, session
from werkzeug.urls import url_parse
from app import app
from app.forms import LoginForm, BasicsForm, DetailsForm
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
@app.route('/basics', methods=['GET', 'POST'])
def basics():
    if not user.auth: # check for login
        return redirect(url_for('login'))
    form = None
    # if the form was already completed then refills in some details. The user will have to re-enter the pipeline/genome (TODO - fix this)
    if 'basics' in session:
        form = BasicsForm(data=session['basics'])
    else:
        form = BasicsForm()
    # form = BasicsForm()
    # was everything filled in correctly?
    if form.validate_on_submit():
        tmp_data = form.data
        # remove unneeded keys
        del tmp_data['csrf_token']
        del tmp_data['next_button']
        # store form data
        session['basics'] = tmp_data
        
        return redirect(url_for('details'))
    return render_template('basics.html', title='Basics', current_user=user, form=form, families=FAMILIES_JSON)

# this page has the particular details based on the pipeline, as well as the data/working directory selection
@app.route('/details', methods=['GET', 'POST'])
def details():
    if not user.auth: # check for login
        return redirect(url_for('login'))

    form = DetailsForm()
    if form.validate_on_submit():
        return redirect(url_for('submit'))
    return render_template('details.html', title='Details', current_user=user, form=form)
    
# the user can review their inputs before submitting the job
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if not user.auth: # check for login
        return redirect(url_for('login'))
    if 'basics' in session:
        flash(session['basics'])
    else:
        flash("You need to fill out the Basics form!")
    return render_template('submit.html', title='Submit', current_user=user)

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
        return redirect(url_for('basics'))
    form = LoginForm()
    if form.validate_on_submit(): # is everything filled in correctly?
        username = form.username.data
        password = form.password.data
        # disabled ssh login for now.
        user.name = username
        user.auth = True
        flash('Login successful')
        return redirect(url_for('basics'))
        '''
        try: # to login
            # will configure ssh later
            # ssh.connect(ip, username=username, password=password)
            user.name = username
            user.auth = True
            flash('Login successful')
            return redirect(url_for('basics'))
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
    if 'basics' in session:
        del session['basics'] # delete the form inputs
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html', current_user=user)