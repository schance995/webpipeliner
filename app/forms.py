from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Regexp, Optional
from app.determinators import getFamilies 

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
    # we'll add a 'select a value' later.
    pipelineFamily = SelectField('Pipeline Family',
                                 choices=[(f.lower(), f) for f in getFamilies()],
                                 validators=[DataRequired()]
                                 )
    # dynamic fields based on value of family: choices are empty so we can initialize them later.
    pipeline = SelectField('Specific Pipeline', choices=[], validators=[DataRequired()])

    genome = SelectField('Genome', choices=[], validators=[DataRequired()])
    
    next = SubmitField('Next')
