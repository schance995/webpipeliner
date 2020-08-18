from collections import namedtuple
from json import dumps

# this is a dictionary of dictionaries! The outer dictionary is for the families, and the inner dictionaries are for the allowed pipelines and genomes for those families.

Family = namedtuple('Family', 'pipelines, genomes')

# follow this format to add a new family
FAMILIES = {}
FAMILIES['ExomeSeq'] = Family(['Initial QC', 'Germline', 'Somatic Tumor-Normal', 'Somatic Tumor-Only'],
                              ['hg19','mm10','hg38'])
FAMILIES['RNASeq'] = Family(['Quality Control Analysis','Differential Expression Analysis','Fusion Detection','Variant Calling'],
                            ['hg19','mm10','mm9','hg38','hs37d5','hs38d1','hg38_30_KSHV','hg38_HPV16','canFam3','Mmul_8.0.1', 'hg38_30', 'mm10_M21'])
FAMILIES['GenomeSeq'] = Family(['Initial QC', 'Germline', 'Somatic Tumor-Normal', 'Somatic Tumor-Only'],
                               ['hg19','mm10','hg38'])
FAMILIES['mir-Seq'] = Family(['miRSeq_v2','CAPmirseq-plus'],
                             ['hg19','mm10','mm9','hg38'])
FAMILIES['ChIPseq'] = Family(['InitialChIPseqQC', 'ChIPseq'],
                             ['hg19','mm10','mm9','hg38','hs37d5','hs38d1','hg38_30_KSHV','hg38_HPV16','canFam3','Mmul_8.0.1', 'hg38_30', 'mm10_M21'])
FAMILIES['scRNAseq'] = Family(['Initial QC','Differential Expression'],
                              ['GRCh38','mm10'])
# keep family JSON stored in memory
d = {}
for fam in list(FAMILIES.keys()):
    d[fam] = FAMILIES[fam]._asdict()

FAMILIES_JSON = dumps(d)

def getFamilies():
    return list(FAMILIES.keys())

# use no argument or "all" to get all pipelines or genomes
def getPipelines(fam="all"):
    if fam == "all":
        res = set()
        for f in list(FAMILIES.keys()):
            res.update(FAMILIES[f].pipelines) # add all pipelines to the set
        return res
    elif fam not in FAMILIES:
        raise ValueError("The family '"+fam+"' is not a valid family.")
    else:
        return FAMILIES[fam].pipelines

def getGenomes(fam="all"):
    if fam == "all":
        res = set()
        for f in list(FAMILIES.keys()):
            res.update(FAMILIES[f].genomes) # add all genomes to the set
        return res
    elif fam not in FAMILIES:
        raise ValueError("The family '"+fam+"' is not a valid family.")
    else:
        return FAMILIES[fam].genomes
