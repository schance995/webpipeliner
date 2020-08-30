from project.custom import NamedFileField
from wtforms import StringField
from wtforms.validators import InputRequired, Length


def add_target_capture_kit(form, genome):
    '''
    Adds a field to specify the target capture kit directory to the specified form.
    '''
    tck = StringField('Target Capture Kit',
        description='By default, the path to the Agilent SureSelect V7 targets file is filled in here',
        validators=[InputRequired(), Length(max=500)],
        default='/data/CCBR_Pipeliner/db/PipeDB/lib/Agilent_SSv7_allExons_hg19.bed')
    setattr(form, 'targetCaptureKit', tck)


def add_fields_somatic_normal(form, genome):
    '''
    Adds a pairs file upload and a target capture kit directory.
    '''
    add_target_capture_kit(form, genome)
    setattr(form, 'pairs', NamedFileField(expect='pairs', required=True))


def get_genomeseq_fields():
    '''
    Returns a dictionary of pipeline names to their respective add functions.
    '''
    res = {}
    res['Initial QC'] = add_target_capture_kit
    res['Germline'] = add_target_capture_kit
    res['Somatic Tumor-Only'] = add_target_capture_kit
    res['Somatic Tumor-Normal'] = add_fields_somatic_normal
    return res