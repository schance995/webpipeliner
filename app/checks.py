from re import match
from os import walk

def valid_filename(filename):
    rgx = '^(.+)\.(R[12]\.fastq\.gz)$'
    m = match(rgx, filename)
    if not m:
        return (False, 'The filename {} should end with R1.fastq.gz or R2.fastq.gz'.format(filename))
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
            err += '\nShould not contain "sample" before {}'.format(m[2])
        if 'R1' in captured:
            err += '\nShould not contain "R1" before {}'.format(m[2])
        if 'R2' in captured:
            err += '\nShould not contain "R2" before {}'.format(m[2])
        if err != '':
            err = 'The filename %s has the following errors %s' % filename, err
        return (err == '', err)

def read_data_dir(path):
        # get only all (base) filenames to simulate the data directory
        (_, _, filenames) = next(walk(path))
        err = ''
        rawdata = {}
        paired_end = False
        if filenames: # empty
            rgx = '^(.*)\.R([12])\.fastq\.gz$'
            for f in filenames:
                valid, e = valid_filename(f)
                if valid: # invalid filename
                    m = match(rgx, f)
                    # store filenames as { name w/o extension: 1 or 2
                    if m[1] in rawdata:
                        rawdata[m[1]].append(m[2])
                    else:
                        rawdata[m[1]] = [m[2]]
                    if m[2] == 2:
                        paired_end = True
                # else:
                #     err = e
                #     break
            pass # to signify end of foor loop
        else:
            err = 'The selected directory is empty.'
        return (rawdata, paired_end, err)

'''
if file is uploaded lines can be read first then sent to the function:
F=open('groups.tab', 'r')
lines=F.readlines()
F.close()
fun(lines) # a list of lines
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
        parts = line.split('\t')
        if len(parts) > 3:
            err = 'There are too many columns on line {}'.format(line_num)
            break
        elif len(parts) < 3:
            err = 'There are not enough columns on line {}'.format(line_num)
            break
        # exactly 3 parts
        sample = parts[0]
        if sample in d:
            err = 'The sample name "{}" on line {} appeared twice'.format(sample, line_num)
            break
        if sample not in samples:
            err = 'The sample name {} on line {} doesn\'t appear in your data directory'.format(sample, line_num)
            break
        d[sample] = parts[1] # group
        labels.append(parts[2].replace('\r', '')) # label. Must replace \r because of silly Windows carriage return (\r\n)
    if err == '':
        groups['rsamps']=list(d.keys())
        groups['rgroups']=set(d.values()) # may be multiple groups
        groups['rlabels']=labels
        # does this dictionary be named exactly this way?
    return (groups, err)

# code to verify groups.tab
# groups.tab must exist, and the groups must exist in groups.tab.
# assuming that a list of groups called groups exists
'''
if file is uploaded then can just read first line
F=open('contrasts.tab', 'r')
line=F.readline() # only need first line
F.close()
'''
def read_contrasts(lines, groups):
    err = ''
    contrasts = []
    line_num = 0
    for line in lines:
        line_num += 1
        parts = line.split('\t')
        if len(parts) > 2:
            err = 'There are too many columns on line {}'.format(line_num)
            break
        elif len(parts) < 2:
            err = 'There are not enough columns on line {}'.format(line_num)
            break

        parts[1] = parts[1].replace('\r', '') # only replacing where we expect \n should be good enough
        if parts[0] and parts[1] in groups:
            contrasts.append(parts) # replace part of array
        else:
            err = 'The groups on line {} don\'t exist in groups.tab'.format(line_num)
            break
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
