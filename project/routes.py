from flask import flash, redirect, render_template, session, url_for
from project import app
from project.forms import BasicsForm, create_details_form
from project.user import User
from project.families import FAMILIES_JSON
from project.checks import read_data_dir, read_file
from json import dumps


user = User()


@app.route('/basics', methods=['GET', 'POST'])
def basics():
    '''
    Webpage for filling out basic information about the pipeline request
    '''
    # if not user.auth: # check for login
    #     return redirect(url_for('login'))
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

    if form.validate_on_submit():
        # copy data onto session
        tmp_data = form.data 
        datapath = tmp_data['dataPath']
        rawdata, paired_end, err, specialfound = read_data_dir(datapath) # directory is relative to app folder
        
        if err: # then directory has 0 relevant files
            flash(err, 'error') 
            return redirect(url_for('basics'))
        else: # report found files
            p_end = 'paired' if paired_end else 'single'
            msg = 'Found {} files in {} ({}-end)'.format(len(rawdata), datapath, p_end)
            flash(msg, 'success')
            for special in specialfound:
                flash('Found {} in {}'.format(special, datapath), 'success')
            tmp_data['rawdata'] = rawdata
            tmp_data['paired_end'] = paired_end

        session['basics'] = tmp_data
        user.basics = True
        return redirect(url_for('details'))

    return render_template('basics.html', title='Basics', current_user=user, form=form, families=FAMILIES_JSON)


def check_form_field(form, field, datatocompare, err, requires=None):
    '''
    Checks a file field for validity, and returns its contents in list or dict format if valid. Else returns None.
    '''
    if hasattr(form, field):
        if form[field].data:
            if (not requires) or form[requires].data:
                file = form[field].data
                data, errors = read_file(file, datatocompare)
                
                if errors:
                    err[0] = True
                    for e in errors:
                        flash(e, 'error')
                else:
                    session['details'][field+'data'] = dumps(data)
            else:
                err[0] = True
                flash('Must upload both {}.tab and {}.tab'.format(field, requires), 'error')
                
            return data
    return None # not an error


@app.route('/details', methods=['GET', 'POST'])
def details():
    '''
    this page has the particular details based on the pipeline, as well as the data/working directory selection
    the user should fill out relevant details in the basics form first. Otherwise they will be redirected to fill out the forms.
    '''
#    if not user.auth: # check for login
#        return redirect(url_for('login'))
    if not user.basics: # basics form must be completed first
        flash("You need to fill out the Basics form before the Details!", 'warning')
        return redirect(url_for('basics'))
    # stored results from basics form
    family = session['basics']['family']
    pipeline = session['basics']['pipeline']
    genome = session['basics']['genome']
    # dynamic form
    form = create_details_form(family, pipeline, genome)
    
    if form.validate_on_submit(): # also checks for valid filenames
        tmp_data = form.data # a deep copy of the data is created

        # do not store actual files in session, not jsonifiable
        for i in ['groups', 'contrasts', 'pairs', 'peakcall', 'contrast']:
            if i in tmp_data:
                del tmp_data[i]
        
        session['details'] = tmp_data
        # load rawdata back into memory for validating inputs
        rawdata = session['basics']['rawdata']

        # groupsjson may already exist
        # groupsdata = None
        # if 'groupsjson' in session['details']: groupsdata = loads(session['details']['groupsjson'])

        errlist = [False]
        # errlist contains boolean describing if any errors occured when reading files
        # pass this in with every check_form_field
        
        groupsdata = check_form_field(form, 'groups', rawdata, errlist)
        if groupsdata:
            groups = groupsdata['groups']
            check_form_field(form, 'contrasts', groups, errlist, requires='groups')

        check_form_field(form, 'pairs', rawdata, errlist)

        peaksdata = check_form_field(form, 'peakcall', rawdata, errlist)
        if peaksdata:
            groups = {row[-1] for row in peaksdata} # get groups
            check_form_field(form, 'contrast', groups, errlist, requires='peakcall')

        # at this point everything is read
        if errlist[0]:
            return redirect(url_for('details'))
        else:
            user.basics = False
            flash('You have submitted your pipeline request, please check your email for the pipeline progress.', 'success')
            # alert the user
            return redirect(url_for('basics'))
    # if form.validate on submit ...
    elif 'details' in session: # what does this do again? I think it preserves prior inputs
        form.process(data=session['details'])

    # flash("Family = " + family + " and Pipeline = " + pipeline + " and Genome = " + genome, 'success')
    return render_template('details.html', title='Details', current_user=user, form=form, header='{}+{}+{}'.format(family, pipeline, genome))


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    This route handles user login.
    To integrate with Flask, add the decorate @login_required in front of the desired routes
    '''
#    if user.auth:
#        return redirect(url_for('basics'))
#    form = LoginForm()
    if not user.auth: #form.validate_on_submit(): # is everything filled in correctly?
        #username = form.username.data
        #password = form.password.data
        user.name = 'login disabled'
        user.auth = True
        user.basics = False
        flash('Logged in. Form progress cleared')
        return redirect(url_for('basics'))


@app.route('/logout')
def logout():
    '''
    This route handles user logout.
    '''
    session.clear()
    flash('Logged out. Session cleared, form progress cleared')
    if user.auth:
        user.auth = False
        user.basics = False
    return redirect(url_for('basics'))


@app.route('/')
@app.route('/about')
def about():
    '''
    The about page. Also the landing page.
    '''
    return render_template('about.html', current_user=user)
