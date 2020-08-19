def create_clustering_resolution():
    return FloatListField('Clustering Resolution(s)',
        default=['0.4','0.6','0.8','1.0','1.2'], # float array
        validators=[DataRequired(), check_float_list])

# scRNAseq
def add_fields_scrna_QC(**kwargs):
    form, genome = kwargs.get('form'), kwargs.get('genome')
    alist = ['SLM (Smart Local Moving)', 'Louvain (Original)', 'Louvain (with Multilevel Refinement)']
    algorithms = SelectField('Clustering algorithm',
        choices=[(a, a) for a in alist])
#        default='SLM (Smart Local Moving)')
    setattr(form, 'clusteringAlgorithm', algorithms)
    setattr(form, 'clusteringResolution', create_clustering_resolution())
    annotHuman = ["Human Primary Cell Atlas","Blueprint/ENCODE","Monaco Immune","Database of Immune Cell Expression (DICE)"]
    annotMouse = ["ImmGen","Mouse RNASeq"]
    annot = {'GRCh38': annotHuman, 'mm10': annotMouse}.get(genome)
    annotations = SelectField('Annotation database',
        choices=[(a, a) for a in annot])
    setattr(form, 'annotationDatabase', annotations)
    setattr(form, 'citeseqIncluded', BooleanField('CITESeq Included'))
    add_sample_info(**kwargs, options={'groups': False, 'contrasts': False})

# form elements are displayed in the same order they are added in
def add_fields_scrna_DE(**kwargs):
    form = kwargs.get('form')
    setattr(form, 'prepatch', BooleanField('Use pre-batch/merged correction'))
    setattr(form, 'postpatch', BooleanField('Use post-batch/integrated correction'))
    setattr(form, 'clusteringResolution', create_clustering_resolution())
    stats = SelectField('Statistical test',
        choices = [(a, a) for a in ['MAST', 'DESeq2', 'Likelihood Ratio', 'Logistic regression', 'Negative Binomial', 'Wilcoxon', 'Student\'s T']],
        default='MAST')
    setattr(form, 'statisticalTest', stats)
    setattr(form, 'minFraction', FloatField('Minimum fraction of cells expressing DE genes', default=0.1, validators=[DataRequired()]))
    setattr(form, 'minFoldChange', FloatField('Minimum fold change to report DE genes', default=0.25, validators=[DataRequired()]))
    add_sample_info(**kwargs, options={'groups': False, 'contrasts': False})