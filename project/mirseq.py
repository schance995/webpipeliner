from project.custom import NamedFileField
from wtforms import BooleanField

def add_fields_mir_CAP(form, genome):
    setattr(form, 'groups', NamedFileField(expect='groups'))
    setattr(form, 'contrasts', NamedFileField(expect='contrasts'))


def add_fields_mir_v2(form, genome):
    setattr(form, 'identifyNovelmiRNAs', BooleanField('Identify Novel miRNAs'))
    add_fields_mir_CAP(form, genome)


def get_mirseq_fields():
    res = {}
    res['CAPmirseq-plus'] = add_fields_mir_CAP
    res['miRSeq_v2'] = add_fields_mir_v2
    return res