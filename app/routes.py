from flask import render_template, flash, redirect, url_for, request, jsonify, session
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from app import app
from app.forms import LoginForm, BasicsForm, create_details_form
import paramiko
from app.user import User
from app.families import getFamilies, getGenomes, getPipelines, FAMILIES_JSON
from app.checks import read_data_dir, read_groups, read_contrasts, read_pairs, read_peaks, read_contrast_
from json import dumps, loads

user = User()

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', current_user=user), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html', current_user=user), 500

@app.route('/')
@app.route('/basics', methods=['GET', 'POST'])
def basics():
#    if not user.auth: # check for login
#        return redirect(url_for('login'))
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
        #del tmp_data['csrf_token']
        #del tmp_data['next_button']
        # store form data

        datapath = 'rawdata' # tmp_data['dataPath'] # hardcoding a directory for test purposes
        rawdata, paired_end, err = read_data_dir(datapath) # directory is relative to app folder
        
        if err: # then directory is empty
            flash(err, 'error') 
            return redirect(url_for('basics'))
        else: # report the number of files found
            p_end = 'paired' if paired_end else 'single'
            msg = 'Found {} files in data directory ({}-end)'.format(len(rawdata), p_end)
            flash(msg, 'success')
            tmp_data['rawdata'] = rawdata
            tmp_data['paired_end'] = paired_end

        session['basics'] = tmp_data
        user.basics = True
        user.details = False # so that they can't just submit right away
        return redirect(url_for('details'))
    
    return render_template('basics.html', title='Basics', current_user=user, form=form, families=FAMILIES_JSON)

# this page has the particular details based on the pipeline, as well as the data/working directory selection
# the user should fill out relevant details in the basics form first. Otherwise they will be redirected to fill out the forms.

@app.route('/details', methods=['GET', 'POST'])
def details():
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
        #del tmp_data['csrf_token']
        #del tmp_data['next_button']
        # do not store actual files in session
        for i in ['groups', 'contrasts', 'pairs', 'peakcall', 'contrast']:
            if i in tmp_data:
                del tmp_data[i]
        err = []
        # merge tmp data with details?

        session['details'] = tmp_data
        # load rawdata back into memory for validating inputs
        rawdata = session['basics']['rawdata']
        # merge dictionaries with tmp_data having priority. user does not have to reupload groups or contrasts if they already did so
        # not sure whether this is a good idea or not
 
        # groupsjson may already exist
        groupsdata = None if 'groupsjson' not in session['details'] else loads(session['details']['groupsjson'])
        # was a file uploaded?
        if hasattr(form, 'groups') and form.groups.data:
            f = form.groups.data
            filename = secure_filename(f.filename) # to prevent cd ../ attacks, and gets the end filename
            # file must be converted from bytes to string
            groupsdata, err = read_groups(f.read().decode('utf-8').split('\n'), rawdata)
            if err:
                for e in err:
                    flash(e, 'error')
                #form.groups.errors.extend(err)
                #return redirect(url_for('details'))
            else:
                session['details']['groupsjson'] = dumps(groupsdata) # add the data for access later

        if hasattr(form, 'contrasts') and form.contrasts.data:
            if groupsdata:
                f = form.contrasts.data
                contrastsdata, err = read_contrasts(f.read().decode('utf-8').split('\n'), groupsdata['rgroups'])
                if err:
                    for e in err:
                        flash(e, 'error')
                    #form.contrasts.errors.extend(err)
                    #return redirect(url_for('details'))
                    #1 / 0
                else:
                    session['details']['contrastsjson'] = dumps(contrastsdata)
            else:
                flash('Must also upload groups.tab in order to define contrasts.tab', 'error')
                #form.groups.errors.append(err)
                #return redirect(url_for('details'))

        #checking other forms. tbd
        if hasattr(form, 'peakcall') and form.peakcall.data:
            f = form.peakcall.data
            peaksdata, err = read_peaks(f.read().decode('utf-8').split('\n'), rawdata)
            if err:
                for e in err:
                    flash(e, 'error')
                #form.pairs.peakcall.extend(err)
            else:
                session['details']['peaksjson'] = dumps(peaksdata)

        if hasattr(form, 'pairs') and form.pairs.data:
            f = form.pairs.data
            pairsdata, err = read_pairs(f.read().decode('utf-8').split('\n'), rawdata)
            print(pairsdata, err)
            if err:
                for e in err:
                    flash(e, 'error')
                #form.pairs.errors.extend(err)
            else:
                session['details']['pairsjson'] = dumps(pairsdata)

        if hasattr(form, 'contrast') and form.contrast.data:
            if peaksdata:
                f = form.contrast.data
                groups_to_check = {row[-1] for row in peaksdata}
                contrast_data, err = read_contrast_(f.read().decode('utf-8').split('\n'), groups_to_check)
                if err:
                    for e in err:
                        flash(e, 'error')
                    #form.pairs.contrast.extend(err)
                else:
                    session['details']['contrast_json'] = dumps(contrast_data)
        else:
            flash('Must also upload peakcall.tab to upload contrast.tab', 'error')
            #form.groups.errors.append(err)
            #return redirect(url_for('details'))
            
        # at this point everything is read and ok
        if err:
            return redirect(url_for('details'))
        else:
            user.details = True
            flash('You have submitted your pipeline request, please check your email for the pipeline progress.', 'success')
            # alert the user
            return redirect(url_for('basics'))
        pass
    # if form.validate on submit ...
    elif 'details' in session: # what does this do again? I think it preserves prior inputs
        form.process(data=session['details'])
    # flash("Family = " + family + " and Pipeline = " + pipeline + " and Genome = " + genome, 'success')
    return render_template('details.html', title='Details', current_user=user, form=form, header='{}+{}+{}'.format(family, pipeline, genome))

@app.route('/login', methods=['GET', 'POST'])
def login():
#    if user.auth:
#        return redirect(url_for('basics'))
#    form = LoginForm()
    if not user.auth: #form.validate_on_submit(): # is everything filled in correctly?
        #username = form.username.data
        #password = form.password.data
        user.name = 'login disabled'
        user.auth = True
        user.basics = False
        user.details = False
        # session['formdata'] = {}
        flash('Logged in. Form progress cleared')
        return redirect(url_for('basics'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out. Session cleared, form progress cleared')
    if user.auth:
        user.auth = False
        user.basics = False
        user.details = False
    return redirect(url_for('basics'))

@app.route('/about')
def about():
    return render_template('about.html', current_user=user)
