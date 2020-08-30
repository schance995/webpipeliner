from project.genomeseq import get_genomeseq_fields


def get_exomeseq_fields():
    '''
    ExomeSeq and GenomeSeq have identical settings at the time of this writing.
    '''
    return get_genomeseq_fields()