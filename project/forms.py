from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, FloatField, IntegerField, Field
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Regexp, Optional, NoneOf, Length, AnyOf, ValidationError
from wtforms.widgets import TextInput
from project.families import getFamilies, getPipelines, getGenomes
from werkzeug.utils import secure_filename


class LoginForm(FlaskForm):
    '''
    Contains fields for a login page.

    Attributes:
        username: username field
        password: password field
        submit: sign in button
    '''
    username = StringField('Username', validators=[DataRequired(), Length(max=500)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Sign In')


class BasicsForm(FlaskForm):
    '''
    Contains fields for basic information needed to submit a pipeline request.

    Attributes:
        dataPath: string field for path to data directory
        workingPath: string field for path to working directory
        family: select field for family
        pipeline: select field for pipeline
        genome: select field for genome
        next_button: button to advance to DetailsForm

    Note on validating select fields:
        While choices are filled dynamically via Javascript (see static/basics.js), validate_choice is False because otherwise the only valid choices are those initialized in choices at startup.
        Instead, the AnyOf validator is used to ensure that the default option and other invalid inputs are not accepted.
    '''
    dataPath = StringField('Enter path to data directory',
                           default='',
                           validators=[DataRequired(), Length(max=500)])

    workingPath = StringField('Enter path to working directory',
                              default='',
                              validators=[DataRequired(), Length(max=500)])

    # choices are (value, label) pairs. But only providing a value makes label = value
    family_choices = [(f, f) for f in getFamilies()]
    family_choices.insert(0, ('Select a family', 'Select a family'))

    family = SelectField('Pipeline Family',
                         choices=family_choices,
                         default='Select a family',
                         validators=[DataRequired(),
                                     NoneOf(['Select a family'],
                                     message='Must select a family')])

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
    '''
    Contains common fields shared by all pipelines.

    Attributes:
        projectId: optional field for a project name
        email: field that accepts well-formed @nih.gov email addresses (but does not check that they are valid)
        flowCellId: optional field for flow cell ID.
        submit_button: button for submitting the finished pipeline request

    To add more fields dynamically:
        Define functions to add additional fields, then assign them to the proper location 
        The functions should accept **kwargs and expect at minimum the keywords form and genome, as they are passed by 
        'form' contains the form.
        'options' is a dict that maps specific fields to True/False depending on whether 
    '''
    projectId = StringField('Project ID',
                            description='Examples: CCBR-nnn,Labname or short project name',
                            validators=[Optional(), Length(max=500)])
    
    email = EmailField('Email',
                        description='Must use @nih.gov email address',
                        validators=[DataRequired(),
                        Regexp('^\w*@nih\.gov$',
                               Length(max=500)],
                               message='Not an @nih.gov email address'))

    flowCellId = StringField('Flow Cell ID',
                             description='FlowCellID, Labname, date or short project name',
                             validators=[Optional(), Length(max=500)])
    
    submit_button = SubmitField('Submit Pipeline Request')

def skip(*args, **kwargs):
    pass
'''
A formal way to do nothing. Used by the function dictionary to add additional forms.
'''

# code to initialize the form functions
formFunctions = {}
for f in getFamilies():
    formFunctions[f] = {p: skip for p in getPipelines(f)}
    # dictionary comprehension: each dictionary has a dictionary inside. family -> pipeline



# all exsomeseq pipelines require this
def add_target_capture_kit(*args, **kwargs):
    form = kwargs.get('form')
    tck = StringField('Target Capture Kit',
        description='By default, the path to the Agilent SureSelect V7 targets file is filled in here',
        validators=[DataRequired(), Length(max=500)],
        default='/data/CCBR_Pipeliner/db/PipeDB/lib/Agilent_SSv7_allExons_hg19.bed')
    setattr(form, 'targetCaptureKit', tck)

def add_fields_somatic_normal(**kwargs):
    add_target_capture_kit(**kwargs)
    add_sample_info(options={'pairs': True}, **kwargs,) # required!

for f in ['ExomeSeq', 'GenomeSeq']: # share the same pipelines
    formFunctions[f]['Initial QC'] = add_target_capture_kit
    formFunctions[f]['Germline'] = add_target_capture_kit
    formFunctions[f]['Somatic Tumor-Only'] = add_target_capture_kit
    formFunctions[f]['Somatic Tumor-Normal'] = add_fields_somatic_normal

# mirseq
def add_fields_mir_CAP(**kwargs):
    add_sample_info(options={'groups': False, 'contrasts': False}, **kwargs)

def add_fields_mir_v2(**kwargs):
    form = kwargs.get('form')
    setattr(form, 'identifyNovelmiRNAs', BooleanField('Identify Novel miRNAs'))
    add_fields_mir_CAP(**kwargs)

formFunctions['mir-Seq']['CAPmirseq-plus'] = add_fields_mir_CAP
formFunctions['mir-Seq']['miRSeq_v2'] = add_fields_mir_v2

# chipseq
def add_fields_chip_QC(**kwargs):
    add_sample_info(options={'peaks': False}, **kwargs)

def add_fields_chip_seq(**kwargs):
    add_sample_info(options={'peaks': True, 'contrast': True}, **kwargs) # required!

formFunctions['ChIPseq']['InitialChIPseqQC'] = add_fields_chip_QC
formFunctions['ChIPseq']['ChIPseq'] = add_fields_chip_seq

formFunctions['scRNAseq']['Initial QC'] = add_fields_scrna_QC
formFunctions['scRNAseq']['Differential Expression'] = add_fields_scrna_DE

# dynamic forms are created here by updating an internal subclass's attributes
def create_details_form(family, pipeline, genome):
    class TemplateDetailsForm(DetailsForm):
        pass

# call the correct function from the dictionary and raise an error if something's not found.
    try:
        formFunctions[family][pipeline](form=TemplateDetailsForm, genome=genome)
    except KeyError as e:
        print(e)

    return TemplateDetailsForm()
