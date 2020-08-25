from project.custom import NamedFileField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, FloatField, IntegerField, Field
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Regexp, Optional, NoneOf, Length, AnyOf, ValidationError
from wtforms.widgets import TextInput

def add_fields_RNA_DEA(form, genome):
    setattr(form, 'reportDiffExpGenes', BooleanField('Report differentially expressed genes'))
    setattr(form, 'groups', NamedFileField(expect='groups'))
    setattr(form, 'contrasts', NamedFileField(expect='contrasts'))


def add_fields_RNA_QCA(form, genome):
    setattr(form, 'groups', NamedFileField(expect='groups'))
    setattr(form, 'contrasts', NamedFileField(expect='contrasts'))


def get_rnaseq_fields():
    res = {}
    res['Differential Expression Analysis'] = add_fields_RNA_DEA
    res['Quality Control Analysis'] = add_fields_RNA_QCA
    return res