import re
def valid_filename(filename):
    rgx = '^(.+)\.(R[12]\.fastq\.gz)$'
    m = re.match(rgx, filename)
    if not m:
        return (False, 'The filename should be <name here>.R1.fastq.gz or R2.fastq.gz')
    else:
        err = ''
        captured = m[1]
        if captured[0].isdigit():
            err += '\nShould not start with a digit'
        if ' ' in captured:
            err += '\nShould not contain a space'
        if '-' in captured:
            err += '\nShould not contain a hyphen/minus sign'
        if 'sample' in captured:
            err += '\nShould not contain "sample" before %s' % m[2]
        if 'R1' in captured:
            err += '\nShould not contain "R1" before %s' % m[2]
        if 'R2' in captured:
            err += '\nShould not contain "R2" before %s' % m[2]
        if err != '':
            err = 'The filename has the following errors:' + err
        return (err == '', err)

'''
if file is uploaded lines can be read first then sent to the function:
F=open('groups.tab', 'r')
lines=F.readlines()
F.close()
fun(lines) # a list of lines
'''
'''
sample inputs
data.dir
Wildtype_S1.R1.fastq.gz
Wildtype_S2.R1.fastq.gz
Knockout_S1.R1.fastq.gz
Knockout_S2.R1.fastq.gz

groups.tab
Wildtype_S1	WT	WT_1
Wildtype_S2	WT	WT_2
Knockout_S1	KO	KO_1
Knockout_S2	KO	KO_2

contrasts.tab
WT	KO
'''
def read_groups(lines, samples):
    # give a list of lines
    d = {} # dictionaries preserve insertion order
    labels = []
    line_num = 0
    groups = {"rsamps":"na", "rgroups":"na", "rlabels":"na"} # default
    err = ''
    for line in lines:
        line_num += 1
        parts = line.split() # this just splits by whitespace. should it split by tabs?
        if len(parts) > 3:
            err = 'There are too many columns on line %s' % line_num
            break
        elif len(parts) < 3:
            err = 'There are too little columns on line %s' % line_num
            break
        # exactly 3 parts
        # assume for now that basename+A and samebasename+A is illegal
        sample = parts[0]
        if sample in d:
            err = 'The sample name "%s" on line %d appeared twice' % sample, line_num
            break
        if sample not in samples:
            err = 'The sample name %s on line %d doesn\'t appear in your data directory' % sample, line_num
            break
        d[sample] = parts[1] # group
        labels.append(parts[2]) # label
    if err == '':
        groups['rsamps']=d.keys()
        groups['rgroups']=d.values()
        groups['rlabels']=labels
        # does this dictionary be named exactly this way?
        # still needs to check for valid groups
    return (groups, err)

# code to verify groups.tab
# assume only 1 line is needed
# groups.tab must exist, and the groups must exist in groups.tab.
# is this a correct assumption?
# assuming that a list of groups called groups exists
'''
if file is uploaded then can just read first line
F=open('contrasts.tab', 'r')
line=F.readline() # only need first line
F.close()
'''
def read_contrasts(line, groups):
    # should line be a single line?
    parts = line.split()
    err = ''
    contrasts = None
    if len(parts) > 2:
        err = 'There are too many columns on line ' + str(line_num)
    elif len(parts) < 3:
        err = 'There are too little columns on line ' + str(line_num)
    else:
        if parts[0] and parts[1] in groups:
            contrasts = parts # replace part of array
        else:
            err = 'The groups in contrasts.tab don\'t exist in groups.tab'
    return (contrasts, err)

# should for now select a local directory to demonstrate that porting code
# shouldn't take too long.

# TESTS
if __name__ == '__main__':
    # are the first 2 valid?
    good_filenames = [
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/Cntrl_S62.R1.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/Cntrl_S62.R2.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/Cntrl_S63.R1.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/Cntrl_S63.R2.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/Cntrl_S64.R1.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/Cntrl_S64.R2.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/Cntrl_S65.R1.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/Cntrl_S65.R2.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/TreatmentA_S66.R1.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/TreatmentA_S66.R2.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/TreatmentA_S67.R1.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/TreatmentA_S67.R2.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/TreatmentA_S68.R1.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/TreatmentA_S68.R2.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/TreatmentA_S69.R1.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/TreatmentA_S69.R2.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/TreatmentB_S70.R1.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/TreatmentB_S70.R2.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/TreatmentB_S71.R1.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/TreatmentB_S71.R2.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/TreatmentB_S72.R1.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/TreatmentB_S72.R2.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/TreatmentB_S73.R1.fastq.gz',
        '/data/CCBR_Pipeliner/testdata/rnaseq/expression_demo/TreatmentB_S73.R2.fastq.gz']
    test = [valid_filename(x) for x in good_filenames]
    assert(False not in [b for (b, dummy) in test])
    
    invalid_filenames = ['.R1.fastq.gz',
                         'R2.fastq.gz',
                         '0test.R1.fastq.gz',
                         'te st.R1.fastq.gz',
                         'sample.R2.fastq.gz',
                         'R2.R2.fastq.gz',
                         'R1.R1.fastq.gz',
                         'min-us.R2.fastq.gz',
                         '5sample-has several eR1rors.R2.fastq.gz']
    test = [valid_filename(x) for x in invalid_filenames]
    assert(True not in [b for (b, dummy) in test])
