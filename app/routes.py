from flask import render_template, flash, redirect, url_for, request, jsonify, session
from werkzeug.urls import url_parse
from app import app
from app.forms import LoginForm, BasicsForm, create_details_form
import paramiko
from app.user import User
from app.families import getFamilies, getGenomes, getPipelines, FAMILIES_JSON
from app.checks import read_data_dir, read_groups, read_contrasts

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
    # if the form was already completed then refills in some details
    if 'basics' in session:
        form = BasicsForm(data=session['basics'])
        saved_pipeline = session['basics']['pipeline']
        form.pipeline.choices.append((saved_pipeline, saved_pipeline))
        saved_genome = session['basics']['genome']
        form.genome.choices.append((saved_genome, saved_genome))
    else:
        form = BasicsForm()
    # was everything filled in correctly?
    if form.validate_on_submit():
        tmp_data = form.data # copy data as we don't need to store csrf I believe
        # remove unneeded keys
        del tmp_data['csrf_token']
        del tmp_data['next_button']
        # store form data
        session['basics'] = tmp_data
        
        return redirect(url_for('details'))
    return render_template('basics.html', title='Basics', current_user=user, form=form, families=FAMILIES_JSON)

# this page has the particular details based on the pipeline, as well as the data/working directory selection
# the user should fill out relevant details in the basics form first. Otherwise they will be redirected to fill out the forms.
@app.route('/details', methods=['GET', 'POST'])
def details():
    if not user.auth: # check for login
        return redirect(url_for('login'))
    if 'basics' not in session: # basics form must be completed first
        flash("You need to fill out the Basics form before the Details!")
        return redirect(url_for('basics'))
    # stored results from basics form
    family = session['basics']['pipelineFamily']
    pipeline = session['basics']['pipeline']
    genome = session['basics']['genome']
    # dynamic form
    form = create_details_form(family, pipeline, genome)
    if form.validate_on_submit():

        tmp_data = form.data # a deep copy of the data is created
        del tmp_data['csrf_token']
        del tmp_data['next_button']
        # should the server or the user store this information?
        session['details'] = tmp_data
        # validate the form ourselves
        
        rawdata, paired_end, err = read_data_dir('rawdata') # directory is relative to app folder
        if err: # reject
            flash(err)
            return redirect(url_for('details'))
        
        groupsdata = None
        if hasattr(form, 'groups') and form.groups.data:
            groupsdata, err = read_groups(form.groups.data.split('\n'), rawdata)
            if err:
                flash(err)
                return redirect(url_for('details'))
        contrastsdata = None
        if hasattr(form, 'contrasts') and form.contrasts.data:
            if groupsdata:
                contrastsdata, err = read_contrasts(form.contrasts.data.split('\n'), groupsdata['rgroups'])
                if err:
                    flash(err)
                    return redirect(url_for('details'))
            else:
                flash('Must define groups in order to define contrasts')
                return redirect(url_for('details'))
        
        # at this point everything is read and ok
        return redirect(url_for('submit'))
    elif 'details' in session:
        form.process(data=session['details'])
    flash("Family = " + family + " and Pipeline = " + pipeline + " and Genome = " + genome)
    return render_template('details.html', title='Details', current_user=user, form=form)
    
# the user can review their inputs before submitting the job
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if not user.auth: # check for login
        return redirect(url_for('login'))
    # user must have completed the basics and details forms before submitting
    if 'basics' in session:
        flash(session['basics'])
    else:
        flash('You need to fill out the Basics form before submitting!')
        return redirect(url_for('basics'))

    if 'details' in session:
        flash(session['details'])
    else:
        flash('You need to fill out the Details form before submitting!')
        return redirect(url_for('details'))
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
    if user.auth:
        user.auth = False
        if 'basics' in session:
            del session['basics'] # delete the form inputs
        if 'details' in session:
            del session['details']
        flash('Logout successful')
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html', current_user=user)
