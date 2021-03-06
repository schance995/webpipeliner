from collections import namedtuple
from json import dumps

'''
This module stores the family, pipeline, and genome names through a dictionary of dictionaries.
The outer dictionary is for the families, and the inner dictionaries are for the allowed pipelines and genomes for those families.
'''

Family = namedtuple('Family', 'pipelines, genomes')

# follow this format to add a new family
FAMILIES = {}
FAMILIES['ExomeSeq'] = Family(['Initial QC', 'Germline', 'Somatic Tumor-Normal', 'Somatic Tumor-Only'],
                              ['hg19', 'mm10', 'hg38'])
FAMILIES['RNASeq'] = Family(['Quality Control Analysis', 'Differential Expression Analysis', 'Fusion Detection', 'Variant Calling'],
                            ['hg19', 'mm10', 'mm9', 'hg38', 'hs37d5', 'hs38d1', 'hg38_30_KSHV', 'hg38_HPV16', 'canFam3', 'Mmul_8.0.1', 'hg38_30', 'mm10_M21'])
FAMILIES['GenomeSeq'] = Family(['Initial QC', 'Germline', 'Somatic Tumor-Normal', 'Somatic Tumor-Only'],
                               ['hg19', 'mm10', 'hg38'])
FAMILIES['mir-Seq'] = Family(['miRSeq_v2', 'CAPmirseq-plus'],
                             ['hg19', 'mm10', 'mm9', 'hg38'])
FAMILIES['ChIPseq'] = Family(['InitialChIPseqQC', 'ChIPseq'],
                             ['hg19', 'mm10', 'mm9', 'hg38', 'hs37d5', 'hs38d1', 'hg38_30_KSHV', 'hg38_HPV16', 'canFam3', 'Mmul_8.0.1', 'hg38_30', 'mm10_M21'])
FAMILIES['scRNAseq'] = Family(['Initial QC', 'Differential Expression'],
                              ['GRCh38', 'mm10'])

# keep family JSON stored in memory
d = {}
for fam in list(FAMILIES.keys()):
    d[fam] = FAMILIES[fam]._asdict()

FAMILIES_JSON = dumps(d)


def getFamilies():
    '''
    Returns a list of families
    '''
    return list(FAMILIES.keys())


def getPipelines(fam="all"):
    '''
    Returns a list of pipelines based on the fam argument.

    Arg:
        fam (str): the family to obtain, defaults to "all"

    Returns:
        A set of all pipelines belonging to the specified family, or all of them if fam == all

    Raises:
        ValueError: if fam is not a valid family
    '''
    if fam == "all":
        res = set()
        for f in list(FAMILIES.keys()):
            res.update(FAMILIES[f].pipelines)  # add all pipelines to the set
        return res
    elif fam not in FAMILIES:
        raise ValueError("The family '" + fam + "' is not a valid family.")
    else:
        return FAMILIES[fam].pipelines


def getGenomes(fam="all"):
    '''
    Returns a list of genome based on the fam argument.

    Arg:
        fam (str): the family to obtain, defaults to "all"

    Returns:
        A set of all genomes belonging to the specified family, or all of them if fam == all

    Raises:
        ValueError: if fam is not a valid family
    '''
    if fam == "all":
        res = set()
        for f in list(FAMILIES.keys()):
            res.update(FAMILIES[f].genomes)  # add all genomes to the set
        return res
    elif fam not in FAMILIES:
        raise ValueError("The family '" + fam + "' is not a valid family.")
    else:
        return FAMILIES[fam].genomes
