from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Regexp, Optional

pipelines = ['Initial QC', 'Germline', 'Somatic Tumor-Normal', 'Somatic Tumor-Only',
                'Quality Control Analysis','Differential Expression Analysis','Fusion Detection','Variant Calling',
                'miRSeq_v2','CAPmirseq-plus',
                'InitialChIPseqQC', 'ChIPseq',
                                       'Initial QC','Differential Expression']
genomes = ['hg19','mm10','mm9','hg38','hs37d5','hs38d1','hg38_30_KSHV','hg38_HPV16','canFam3','Mmul_8.0.1', 'hg38_30', 'mm10_M21']

families = ['ExomeSeq', 'RNAseq', 'GenomeSeq', 'miR-Seq', 'ChIPseq', 'scRNAseq']

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class BasicsForm(FlaskForm):
    projectId = StringField('Project ID',
                            default='project',
                            description='Examples: CCBR-nnn,Labname or short project name',
                            validators=[Optional()]
                            )
    
    # must use regexp to verify @nih.gov specifically
    email = StringField('Email',
                       description='Must use @nih.gov email address)',
                       validators=[DataRequired(),
                                   Regexp('^\w*@nih\.gov$',
                                          message='Not an @nih.gov email address')
                       ])

    flowCellId = StringField('Flow Cell ID',
                             default='stats',
                             description='FlowCellID, Labname, date or short project name',
                             validators=[Optional()]
                        )
    # choices are (key, value) pairs
    pipelineFamily = SelectField('Pipeline Family',
                                 choices=[(x.lower(), x) for x in families],
                                 validators=[DataRequired()]
                                 )
    # for now I'll just have multiple select fields - later I can try to make them dynamic
    pipeline = SelectField('Specific Pipeline',
                           choices=[(x.lower(), x) for x in pipelines],
                           validators=[DataRequired()]
    )

    genome = SelectField('Genome',
                         choices=[(x.lower(), x) for x in genomes],
                         validators=[DataRequired()]
                         )
    
    next = SubmitField('Next')
