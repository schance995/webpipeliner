from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, FloatField, IntegerField
from wtforms.validators import DataRequired, Regexp, Optional, NoneOf, Length, AnyOf, ValidationError
from app.families import getFamilies, getPipelines, getGenomes 

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class BasicsForm(FlaskForm):
    projectId = StringField('Project ID',
        description='Examples: CCBR-nnn,Labname or short project name',
        validators=[Optional(), Length(max=500)],
        render_kw={"placeholder": "project"}) # suggested value
    
    # must use regexp to verify @nih.gov specifically
    email = StringField('Email',
        description='Must use @nih.gov email address',
        validators=[DataRequired(),
        Regexp('^\w*@nih\.gov$', message='Not an @nih.gov email address')])

    flowCellId = StringField('Flow Cell ID',
        description='FlowCellID, Labname, date or short project name',
        validators=[Optional(), Length(max=500)],
        render_kw={"placeholder": "stats"}) # suggested value

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
'''
def validate_filename(shouldbe):
    def _validate_filename(form, field):
        if field.data and field.data.filename != shouldbe:
            raise ValidationError('Filename should match ' + filenam)
    return _validate_filename()
'''

def skip(*optional):
    pass

# code to initialize the form functions
formFunctions = {}
for f in getFamilies():
    formFunctions[f] = {p: skip for p in getPipelines(f)}
    # dictionary comprehension: each dictionary has a dictionary inside. family -> pipeline
    # by default a family/pipeline are assigned to do nothing.

# IMPORTANT: for forms that require extra fields, define functions here to add them.
def add_sample_info(form, *infos):
    filefield = lambda title: FileField('Upload {} (optional)'.format(title), validators=[Optional()])
    if 'groups' in infos:
        setattr(form, 'groups', filefield('groups'))
    if 'contrasts' in infos:
        setattr(form, 'contrasts', filefield('contrasts'))
    if 'peaks' in infos:
        setattr(form, 'peaks', filefield('peaks'))
    if 'pairs' in infos:
        setattr(form, 'pairs', filefiled('pairs'))

# differential expression analysis
def add_fields_RNA_DEA(form):
    setattr(form, 'reportDiffExpGenes', BooleanField('Report differentially expressed genes'))
    add_sample_info(form, 'groups', 'contrasts')

# quality control analysis
def add_fields_RNA_QCA(form):
    add_sample_info(form, 'groups')

formFunctions['RNASeq']['Differential Expression Analysis'] = add_fields_RNA_DEA
formFunctions['RNASeq']['Quality Control Analysis'] = add_fields_RNA_QCA

# all exsomeseq pipelines require this
def add_target_capture_kit(form):
    tck = StringField('Target Capture Kit',
        description='By default, the path to the Agilent SureSelect V7 targets file is filled in here',
        validators=[DataRequired(), Length(max=500)],
        default='/data/CCBR_Pipeliner/db/PipeDB/lib/Agilent_SSv7_allExons_hg19.bed')
    setattr(form, 'targetCaptureKit', tck)

def add_fields_somatic_normal(form):
    add_target_capture_kit(form)
    add_sample_info(form, 'pairs')

for f in ['ExomeSeq', 'GenomeSeq']: # share the same pipelines
    formFunctions[f]['Initial QC'] = add_target_capture_kit
    formFunctions[f]['Germline'] = add_target_capture_kit
    formFunctions[f]['Somatic Tumor-Only'] = add_target_capture_kit
    formFunctions[f]['Somatic Tumor-Normal'] = add_fields_somatic_normal

# mirseq
def add_fields_mir_CAP(form):
    add_sample_info(form, 'groups', 'contrasts')

def add_fields_mir_v2(form):
    add_fields_mir_CAP(form)
    setattr(form, 'identifyNovelmiRNAs', BooleanField('Identify Novel miRNAs')

formFunctions['mir-Seq']['CAPmirseq-plus'] = add_fields_mir_CAP(form)
formFunctions['mir-Seq']['miRSeq_v2'] = add_fields_mir_v2(form)

# chipseq
def add_fields_chip_QC(form):
    add_sample_info(form, 'peaks')

def add_fields_chip_seq(form):
    add_sample_info(form, 'peaks', 'groups')

formFunctions['ChIPseq']['InitialChIPseqQC'] = add_fields_chip_QC(form)
formFunctions['ChIPseq']['ChIPseq'] = add_fields_chip_seq(form)

class FloatListField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return u', '.join(self.data)
        else:
            return u''
    # should be already validated when called
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [float(x.strip()) for x in valuelist[0].split(',')]
        else:
            self.data = []

def check_float_list(form, field):
    for x in field.data.split(','):
        if type(x) != float:
            raise ValidationError('Must be a comma-separated list of floats')

def create_clustering_resolution(form):
    return FloatListField('Clustering Resolution(s)',
        default='0.4, 0.6, 0.8, 1.0, 1.2',
        validators=[DataRequired(), check_float_list])

# scRNAseq
def add_fields_scrna_QC(form):
    algorithms = SelectField('Clustering algorithm',
        choices=['SLM (Smart Local Moving)', 'Louvain (Original)', 'Louvain (with Multilevel Refinement)'],
        default='SLM (Smart Local Moving)')
    setattr(form, 'clusteringAlgorithm', algorithms)
    setattr(form, 'clusteringResolution', create_clustering_resolution(form))
    annotations = SelectField('Annotation database',
        choices=['ImmGen', 'Mouse RNASeq'],
        default='ImmGen')
    setattr(form, 'annotationDatabase', annotations)
    setattr(form, 'citeseqIncluded', BooleanField('CITESeq Included')
    add_sample_info(form, 'groups', 'contrasts')

def add_fields_scrna_DE(form): 
    setattr(form, 'prepatch', BooleanField('Use pre-batch/merged correction')
    setattr(form, 'postpatch', BooleanField('Use post-batch/integrated correction')
    setattr(form, 'clusteringResolution', create_clustering_resolution(form))
    stats = SelectField('Statistical test',
        choices = ['MAST', 'DESeq2', 'Likelihood Ratio', 'Logistic regression', 'Negative Binomial', 'Wilcoxon', 'Student\'s T'],
        default='MAST')
    setattr(form, 'statisticalTest', stats)
    setattr(form, 'minFraction', FloatField('Minimum fraction of cells expressing DE genes', default=0.1, validators=[DataRequired()]))
    setattr(form, 'minFoldChange', FloatField('Minimum fold change to report DE genes', default=0.25, validators=[DataRequired()]))
    add_sample_info(form, 'groups', 'contrasts')

formFunctions['scRNAseq']['Initial QC'] = add_fields_scrna_QC(form)
formFunctions['scRNAseq']['Differential Expression'] = add_fields_scrna_QC(form)


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
