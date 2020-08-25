from project.custom import NamedFileField
from wtforms import StringField


def add_target_capture_kit(form):
    tck = StringField('Target Capture Kit',
        description='By default, the path to the Agilent SureSelect V7 targets file is filled in here',
        validators=[DataRequired(), Length(max=500)],
        default='/data/CCBR_Pipeliner/db/PipeDB/lib/Agilent_SSv7_allExons_hg19.bed')
    setattr(form, 'targetCaptureKit', tck)


def add_fields_somatic_normal(form, genome):
    add_target_capture_kit(form)
    setattr(form, 'pairs', NamedFileField(expect='pairs', required=True))


def get_genomeseq_fields():
    res = {}
    res['Initial QC'] = add_target_capture_kit
    res['Germline'] = add_target_capture_kit
    res['Somatic Tumor-Only'] = add_target_capture_kit
    res['Somatic Tumor-Normal'] = add_fields_somatic_normal
    return res