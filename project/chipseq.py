from project.custom import NamedFileField


def add_fields_chip_QC(form, genome):
    '''
    Adds a pairs form field.
    '''
    setattr(form, 'pairs', NamedFileField(expect='pairs'))


def add_fields_chip_seq(form, genome):
    '''
    Adds a peakcall and contrast form field (both required).
    '''
    setattr(form, 'peakcall', NamedFileField(expect='peakcall', required=True))
    setattr(form, 'contrast', NamedFileField(expect='contrast', required=True))


def get_chipseq_fields():
    '''
    Returns a dictionary of pipeline names to their respective add functions.
    '''
    res = {}
    res['InitialChIPseqQC'] = add_fields_chip_QC
    res['ChIPseq'] = add_fields_chip_seq
    return res