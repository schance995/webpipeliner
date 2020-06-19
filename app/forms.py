from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Regexp, Optional, NoneOf, Length
from app.families import getFamilies 

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class BasicsForm(FlaskForm):
    projectId = StringField('Project ID',
#                            default='project',
                            description='Examples: CCBR-nnn,Labname or short project name',
                            validators=[Optional(), Length(max=500)]
                            )
    
    # must use regexp to verify @nih.gov specifically
    email = StringField('Email',
                       description='Must use @nih.gov email address',
                       validators=[DataRequired(),
                                   Regexp('^\w*@nih\.gov$',
                                          message='Not an @nih.gov email address')
                       ])

    flowCellId = StringField('Flow Cell ID',
#                             default='stats',
                             description='FlowCellID, Labname, date or short project name',
                             validators=[Optional(), Length(max=500)]
                        )
    # choices are (value, label) pairs. But only providing a value makes label = value
    family_choices = [(f, f) for f in getFamilies()]
    family_choices.insert(0, ('Select a family', 'Select a family'))
    pipelineFamily = SelectField('Pipeline Family',
                                 choices=family_choices,
                                 default='Select a family',
                                 validators=[DataRequired(), NoneOf(['Select a family'], message='Must select a family')])
                                 
    # dynamic fields based on value of family: choices are empty so we can initialize them later.
    # validate_choice is False because other inputs will by dynamically added via javascript. But the NoneOf validator will still run,
    # ensuring that the default option is not selectable
    pipeline = SelectField('Specific Pipeline',
                            choices=[('Select a pipeline', 'Select a pipeline')],
                            default='Select a pipeline',
                            validate_choice=False,
                            validators=[NoneOf(['Select a pipeline'], message='Must select a pipeline')])
                            
    genome = SelectField('Genome',
                            validate_choice=False,
                            choices=[('Select a genome', 'Select a genome')],
                            default='Select a genome',
                            validators=[NoneOf(['Select a genome'], message='Must select a genome')])
    
    next_button = SubmitField('Next')

class DetailsForm(FlaskForm):
    next_button = SubmitField('Next')