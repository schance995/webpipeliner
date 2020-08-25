from project.custom import NamedFileField


def add_fields_chip_QC(form, genome):
    setattr(form, 'pairs', NamedFileField(expect='peaks'))


def add_fields_chip_seq(form, genome):
    setattr(form, 'peakcall', NamedFileField(expect='peakcall', required=True))
    setattr(form, 'contrast', NamedFileField(expect='contrast', required=True))


def get_chipseq_fields():
    res = {}
    res['InitialChIPseqQC'] = add_fields_chip_QC
    res['ChIPseq'] = add_fields_chip_seq
    return res