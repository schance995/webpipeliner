from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, FloatField, IntegerField, Field
from wtforms.validators import DataRequired, Regexp, Optional, NoneOf, Length, AnyOf, ValidationError
from wtforms.widgets import TextInput
from app.families import getFamilies, getPipelines, getGenomes
from werkzeug.utils import secure_filename

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=500)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Sign In')

class BasicsForm(FlaskForm):
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
    projectId = StringField('Project ID',
        description='Examples: CCBR-nnn,Labname or short project name',
        validators=[Optional(), Length(max=500)])
        #render_kw={"placeholder": "project"}) # suggested value
    
    # must use regexp to verify @nih.gov specifically
    email = StringField('Email',
        description='Must use @nih.gov email address',
        validators=[DataRequired(),
        Regexp('^\w*@nih\.gov$', message='Not an @nih.gov email address'),
        Length(max=500)])

    flowCellId = StringField('Flow Cell ID',
        description='FlowCellID, Labname, date or short project name',
        validators=[Optional(), Length(max=500)])
        #render_kw={"placeholder": "stats"}) # suggested value
    next_button = SubmitField('Next')

# do nothing
def skip(*args, **kwargs):
    pass

# code to initialize the form functions
formFunctions = {}
for f in getFamilies():
    formFunctions[f] = {p: skip for p in getPipelines(f)}
    # dictionary comprehension: each dictionary has a dictionary inside. family -> pipeline
    # by default a family/pipeline are assigned to do nothing.

# IMPORTANT: for forms that require extra fields, define functions here to add them.
# the genome and form are passed in **kwargs, pass **kwargs as a parameter to any sub-functions
# most functions do not require the 'genome' parameter but it is included for completeness in case functionality needs to be extended
# form, genome = kwargs.get('form'), kwargs.get('genome')
# use get to more gracefully handle bad input (returns None)

def check_file_field(shouldbe, message=None):
    if not message:
        message = 'Filename must match {} exactly'.format(shouldbe)
    def _check_file_field(form, field):
        filename = secure_filename(field.data.filename) # to prevent cd ../ attacks, and gets the end filename
        if filename != shouldbe:
            raise ValidationError(message)
    return _check_file_field

def file_field(title, required):
    label = 'Upload ' + title + '.tab'
    validators = []
    if required:
        validators.append(DataRequired())
        label += ' (required)'
    else:
        validators.append(Optional())
        label += ' (optional)'
    validators.append(check_file_field(title+'.tab'))
    return FileField(label, validators)
    # filename and contents validation should be performed in routes.py

def add_sample_info(**kwargs):
    form = kwargs.get('form')
    options = kwargs.get('options')
    if options: # input should be a dictionary that lists whether the form input is required
        if 'groups' in options:
            setattr(form, 'groups', file_field('groups', options['groups']))
        if 'contrasts' in options:
            setattr(form, 'contrasts', file_field('contrasts', options['contrasts']))
        if 'peaks' in options:
            setattr(form, 'peakcall', file_field('peakcall', options['peaks']))
        if 'pairs' in options:
            setattr(form, 'pairs', file_field('pairs', options['pairs']))
        if 'contrast' in options:
            setattr(form, 'contrast', file_field('contrast', options['contrast']))

# differential expression analysis
def add_fields_RNA_DEA(**kwargs):
    form = kwargs.get('form')
    setattr(form, 'reportDiffExpGenes', BooleanField('Report differentially expressed genes'))
    add_sample_info(options={'groups': False, 'contrasts': False}, **kwargs)

# quality control analysis
def add_fields_RNA_QCA(**kwargs):
    add_sample_info(options={'groups': False}, **kwargs)

formFunctions['RNASeq']['Differential Expression Analysis'] = add_fields_RNA_DEA
formFunctions['RNASeq']['Quality Control Analysis'] = add_fields_RNA_QCA

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

class FloatListField(Field):
    widget = TextInput()
    # reads default value from a literal float list and returns a comma-separated string
    def _value(self):
        if self.data:
            return ', '.join(self.data)
#            return str(self.data).strip('[]')
        else:
            return ''
    # called at form submission but before validation
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [x.strip() for x in valuelist[0].split(',')]
        else:
            self.data = []

# custom validator for this one task
def check_float_list(form, field):
    for x in field.data:
        try:
            float(x)
        except ValueError:
            raise ValidationError('Must be a comma-separated list of floats')

def create_clustering_resolution():
    return FloatListField('Clustering Resolution(s)',
        default=[0.4,0.6,0.8,1.0,1.2], # float array
        validators=[DataRequired(), check_float_list])

# scRNAseq
def add_fields_scrna_QC(**kwargs):
    form, genome = kwargs.get('form'), kwargs.get('genome')
    alist = ['SLM (Smart Local Moving)', 'Louvain (Original)', 'Louvain (with Multilevel Refinement)']
    algorithms = SelectField('Clustering algorithm',
        choices=[(a, a) for a in alist])
#        default='SLM (Smart Local Moving)')
    setattr(form, 'clusteringAlgorithm', algorithms)
    setattr(form, 'clusteringResolution', create_clustering_resolution())
    annotHuman = ["Human Primary Cell Atlas","Blueprint/ENCODE","Monaco Immune","Database of Immune Cell Expression (DICE)"]
    annotMouse = ["ImmGen","Mouse RNASeq"]
    annot = {'CRCh38': annotHuman, 'mm10': annotMouse}.get(genome)
    annotations = SelectField('Annotation database',
        choices=[(a, a) for a in annot])
    setattr(form, 'annotationDatabase', annotations)
    setattr(form, 'citeseqIncluded', BooleanField('CITESeq Included'))
    add_sample_info(**kwargs, options={'groups': False, 'contrasts': False})

# form elements are displayed in the same order they are added in
def add_fields_scrna_DE(**kwargs):
    form = kwargs.get('form')
    setattr(form, 'prepatch', BooleanField('Use pre-batch/merged correction'))
    setattr(form, 'postpatch', BooleanField('Use post-batch/integrated correction'))
    setattr(form, 'clusteringResolution', create_clustering_resolution())
    stats = SelectField('Statistical test',
        choices = [(a, a) for a in ['MAST', 'DESeq2', 'Likelihood Ratio', 'Logistic regression', 'Negative Binomial', 'Wilcoxon', 'Student\'s T']],
        default='MAST')
    setattr(form, 'statisticalTest', stats)
    setattr(form, 'minFraction', FloatField('Minimum fraction of cells expressing DE genes', default=0.1, validators=[DataRequired()]))
    setattr(form, 'minFoldChange', FloatField('Minimum fold change to report DE genes', default=0.25, validators=[DataRequired()]))
    add_sample_info(**kwargs, options={'groups': False, 'contrasts': False})

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
