from project.custom import NamedFileField


def add_fields_chip_QC(form, genome):
    setattr(form, 'pairs', NamedFileField(expect='peaks'))


def add_fields_chip_seq(form, genome):
    setattr(form, 'peaks', NamedFileField(expect='peaks', required=True))
    setattr(form, 'contrasts', NamedFileField(expect='contrasts', required=True))


def get_chipseq_fields():
    res = {}
    res['InitialChIPseqQC'] = add_fields_chip_QC
    res['ChIPseq'] = add_fields_chip_seq
    return res