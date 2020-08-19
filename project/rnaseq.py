from custom import NamedFileField

def add_fields_RNA_DEA(**kwargs):
    form = kwargs.get('form')
    setattr(form, 'reportDiffExpGenes', BooleanField('Report differentially expressed genes'))
    add_sample_info(options={'groups': False, 'contrasts': False}, **kwargs)

# quality control analysis
def add_fields_RNA_QCA(**kwargs):
    add_sample_info(options={'groups': False}, **kwargs)

formFunctions['RNASeq']['Differential Expression Analysis'] = add_fields_RNA_DEA
formFunctions['RNASeq']['Quality Control Analysis'] = add_fields_RNA_QCA