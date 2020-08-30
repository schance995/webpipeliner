from project.custom import NamedFileField
from wtforms import BooleanField

def add_fields_RNA_DEA(form, genome):
    '''
    Adds a checkbox for reporting differential expressed genes and entries for groups and contrasts.
    '''
    setattr(form, 'reportDiffExpGenes', BooleanField('Report differentially expressed genes'))
    setattr(form, 'groups', NamedFileField(expect='groups'))
    setattr(form, 'contrasts', NamedFileField(expect='contrasts'))


def add_fields_RNA_QCA(form, genome):
    '''
    Adds entries for groups and contrasts.
    '''
    setattr(form, 'groups', NamedFileField(expect='groups'))
    setattr(form, 'contrasts', NamedFileField(expect='contrasts'))


def get_rnaseq_fields():
    '''
    Returns a dictionary of pipeline names to their respective add functions.
    '''
    res = {}
    res['Differential Expression Analysis'] = add_fields_RNA_DEA
    res['Quality Control Analysis'] = add_fields_RNA_QCA
    return res