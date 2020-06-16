# this is called "determinators" because these values determinte the dynamic form fields and webpages

# this is a dictionary of dictionaries! The outer dictionary is for the families, and the inner dictionaries are for the allowed pipelines and genomes for those families.
class Family:
    def __init__(self, pipelines, genomes):
        self.pipelines = pipelines
        self.genomes = genomes

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
def getFamilies():
    return list(FAMILIES.keys())

def getPipelines(fam):
    if fam not in FAMILIES:
        raise ValueError("The family '"+fam+"' is not a valid family.")
    else:
        return FAMILIES[fam].pipelines

def getGenomes(fam):
    if fam not in FAMILIES:
        raise ValueError("The family '"+fam+"' is not a valid family.")
    else:
        return FAMILIES[fam].genomes
