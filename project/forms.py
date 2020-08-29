from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, FloatField, IntegerField, Field
from wtforms.fields.html5 import EmailField
from wtforms.validators import AnyOf, DataRequired, Length, NoneOf, Optional, Regexp
from project.families import getFamilies, getPipelines, getGenomes
from project.scrnaseq import get_scrnaseq_fields
from project.rnaseq import get_rnaseq_fields
from project.mirseq import get_mirseq_fields
from project.genomeseq import get_genomeseq_fields
from project.exomeseq import get_exomeseq_fields
from project.chipseq import get_chipseq_fields


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
                                    Regexp('^\w*@nih\.gov$', message='Not an @nih.gov email address'),


    flowCellId = StringField('Flow Cell ID',
                             description='FlowCellID, Labname, date or short project name',
                             validators=[Optional(), Length(max=500)])

    submit_button = SubmitField('Submit Pipeline Request')

def skip(*args, **kwargs):
    '''
    A formal way to do nothing. Used by the function dictionary to add additional forms.
    '''
    pass

# code to initialize the form functions, each imported from their respective py file
formFunctions = {}
formFunctions['ExomeSeq'] = get_exomeseq_fields()
formFunctions['ChIPseq'] = get_chipseq_fields()
formFunctions['GenomeSeq'] = get_genomeseq_fields()
formFunctions['mir-Seq'] = get_mirseq_fields()
formFunctions['RNASeq'] = get_rnaseq_fields()
formFunctions['scRNAseq'] = get_scrnaseq_fields()

# any valid combinations without a py file automatically get skip (no action)
for f in getFamilies():
    for p in getPipelines(f):
        if p not in formFunctions[f]:
            formFunctions[f][p] = skip

# dynamic forms are created here by updating an internal subclass's attributes
def create_details_form(family, pipeline, genome):
    '''
    Returns a form with custom fields depending on the specified family, pipeline, and genome.
    
    Args:
        family (str): The name must be an exact match.
        pipeline (str): The name must be an exact match.
        genome (str): The name must be an exact match. Not used by all pipelines but included for completeness.

    Returns:
        TemplateDetailsForm(form): The custom form with new fields added

    To add a new combination of family/pipeline/genome:
        1. Update families.py with the new family and pipeline.
        2. Add formFunctions['pipeline'] = function_to_get_fields() by the formFunctions section.
        3. If a new family was added: create a new py file for that family, and import it at the top of this file.
        4. Inside the family's py file, add a new function to add fields to the form.
               It should be similar to add_function(form, genome) where form and genome will be passed in by this function.
               Use setattr to adjust the form and add new inputs. You can also define custom fields as needed.
        5. Also inside the family's py file, add/update the function_to_get_fields() to map the pipeline name to the function
               that was created in the previous step.
               Return the dictionary with the mapping of pipeline names to adding functions.
    '''
    class TemplateDetailsForm(DetailsForm):
        pass

# call the correct function from the dictionary and raise an error if something's not found.
    try:
        formFunctions[family][pipeline](form=TemplateDetailsForm, genome=genome)
    except KeyError as e:
        raise KeyError('Did not find {} or {} in families or pipelines'.format(family, pipeline))

    return TemplateDetailsForm()
