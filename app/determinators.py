# this is called "determinators" because these values determinte the dynamic form fields and webpages

# this is a dictionary of dictionaries! The outer dictionary is for the families, and the inner dictionaries are for the allowed pipelines and genomes for those families.
FAMILIES = {
    'Select the family': None,
    'ExomeSeq': {
	'pipelines': ['Select the pipeline', 'Initial QC', 'Germline', 'Somatic Tumor-Normal', 'Somatic Tumor-Only'],
	'genomes': ['Select the genome', 'hg19','mm10','hg38']
    },
    'RNAseq': {
	'pipelines': ['Select the pipeline', 'Quality Control Analysis','Differential Expression Analysis','Fusion Detection','Variant Calling'],
	'genomes': ['Select the genome', 'hg19','mm10','mm9','hg38','hs37d5','hs38d1','hg38_30_KSHV','hg38_HPV16','canFam3','Mmul_8.0.1', 'hg38_30', 'mm10_M21']
    },
    'GenomeSeq': {
	'pipelines': ['Select the pipeline', 'Initial QC', 'Germline', 'Somatic Tumor-Normal', 'Somatic Tumor-Only'],
	'genomes': ['Select the genome', 'hg19','mm10','hg38']
    },
    'miR-Seq': {
	'pipelines': ['Select the pipeline', 'miRSeq_v2','CAPmirseq-plus'],
	'genomes': ['Select the genome', 'hg19','mm10','mm9','hg38']
    },
    'ChIPseq': {
	'pipelines': ['Select the pipeline', 'InitialChIPseqQC', 'ChIPseq'],
	'genomes': ['Select the genome', 'hg19','mm10','mm9','hg38','hs37d5','hs38d1','hg38_30_KSHV','hg38_HPV16','canFam3','Mmul_8.0.1', 'hg38_30', 'mm10_M21']
    },
    'scRNAseq': {
	'pipelines': ['Select the pipeline', 'Initial QC','Differential Expression'],
	'genomes': ['Select the genome', 'GRCh38','mm10']
    }
}

def getFamilies():
    return list(FAMILIES.keys())

def getPipelines(fam):
    if fam not in FAMILIES:
        raise ValueError("The family '"+fam+"' is not a valid family.")
    elif fam == 'Select the pipeline':
        raise ValueError("You can't select the \"select\" option.")
    else:
        return FAMILIES[fam]['pipelines']

def getGenomes(fam):
    if fam not in FAMILIES:
        raise ValueError("The family '"+fam+"' is not a valid family.")
    elif fam == 'Select the pipeline':
        raise ValueError("You can't select the \"select\" option.")
    else:
        return FAMILIES[fam]['genomes']

