from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, FloatField, IntegerField
from wtforms.validators import DataRequired, Regexp, Optional, NoneOf, Length, AnyOf
from app.families import getFamilies, getPipelines, getGenomes 

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class BasicsForm(FlaskForm):
    projectId = StringField('Project ID',
                            description='Examples: CCBR-nnn,Labname or short project name',
                            validators=[Optional(), Length(max=500)],
                            render_kw={"placeholder": "project"} # suggested value
                            )
    
    # must use regexp to verify @nih.gov specifically
    email = StringField('Email',
                       description='Must use @nih.gov email address',
                       validators=[DataRequired(),
                                   Regexp('^\w*@nih\.gov$',
                                          message='Not an @nih.gov email address')
                       ])

    flowCellId = StringField('Flow Cell ID',
                             description='FlowCellID, Labname, date or short project name',
                             validators=[Optional(), Length(max=500)],
                             render_kw={"placeholder": "stats"} # suggested value
                        )
    # choices are (value, label) pairs. But only providing a value makes label = value
    family_choices = [(f, f) for f in getFamilies()]
    family_choices.insert(0, ('Select a family', 'Select a family'))
    pipelineFamily = SelectField('Pipeline Family',
                                 choices=family_choices,
                                 default='Select a family',
                                 validators=[DataRequired(), NoneOf(['Select a family'], message='Must select a family')])
                                 
    # dynamic fields based on value of family: choices are empty so we can initialize them later.
    # validate_choice is False because other inputs will by dynamically added via javascript. But the AnyOf validator will still run,
    # ensuring that the default option is not selectable. AnyOf is used to prevent malicious form inputs.
    # adding all the choices here is required. Although they will be removed during the dynamic javascript, flask still needs to validate the choices internally
    # this also allows for restoring of the form if the user presses the back button or clicks on the basics tab
    pipeline = SelectField('Specific Pipeline',
                            choices=[('Select a pipeline', 'Select a pipeline')],
                            default='Select a pipeline',
                            validate_choice=False,
                            validators=[AnyOf(getPipelines(),
                                        message='Must select a pipeline')])
    
    genome = SelectField('Genome',
                            choices=[('Select a genome', 'Select a genome')],
                            default='Select a genome',
                            validate_choice=False,
                            validators=[AnyOf(getGenomes(),
                                        message='Must select a genome')])
    
    next_button = SubmitField('Next')

class DetailsForm(FlaskForm):
    dataDirSelect = BooleanField('Data Dir to be implemented')
    workingDirSelect = BooleanField('Working Dir to be implemented')
    next_button = SubmitField('Next')

# leaving it this way as there may be some more stuff to add later
def addSampleInfo(form, *infos):
    if 'groups' in infos:
        setattr(form, 'groups', TextAreaField('Set groups', render_kw={"placeholder": "Some sample format"}, validators=[Optional()]))
    if 'contrasts' in infos:
        setattr(form, 'contrasts', TextAreaField('Set contrasts', render_kw={"placeholder": "Some other sample format"}, validators=[Optional()]))
    if 'peaks' in infos:
        setattr(form, 'peaks', TextAreaField('Set peaks', render_kw={"placeholder": "Another sample format"}, validators=[Optional()]))

def skip(*optional):
    pass

# IMPORTANT: for forms that require extra fields, define functions here to add them.

# differential expression analysis
def addFieldsRNA_DEA(form):
    setattr(form, 'reportDiffExpGenes', BooleanField('Report differentially expressed genes'))
    setattr(form, 'minCPM', FloatField(label=None, id='minCPM', validators=[DataRequired()]))
    setattr(form, 'minSamples', IntegerField(id='minSamples', validators=[DataRequired()]))
    addSampleInfo(form, 'groups', 'contrasts')

# code to initialize the form functions

formFunctions = {}
for f in getFamilies():
    formFunctions[f] = {p: skip for p in getPipelines(f)}
    # dictionary comprehension: each dictionary has a dictionary inside. family -> pipeline
    # by default a family/pipeline are assigned to do nothing.

# add specific form functions
formFunctions['RNASeq']['Differential Expression Analysis'] = addFieldsRNA_DEA

# dynamic forms are created here by updating an internal subclass's attributes
def create_details_form(family, pipeline, genome):
    class TemplateDetailsForm(DetailsForm):
        pass

# call the correct function from the dictionary and raise an error if something's not found.
    try:
        formFunctions[family][pipeline](TemplateDetailsForm)
    except KeyError as e:
        print(e)

    return TemplateDetailsForm()
