from re import match
from os import walk
from numbers import Number

# json dumps happens in routes
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
                    print(m[1], m[2])
                    # store filenames as { name w/o extension: 1 or 2
                    # m[1] matches sample name
                    # m[2] matches 1 or 2
                    if m[1] in rawdata:
                        rawdata[m[1]].append(m[2])
                    else:
                        rawdata[m[1]] = [m[2]]
                    if m[2] == '2':
                        paired_end = True
                # else:
                #     err = e
                #     break
            pass # to signify end of foor loop
        else:
            err = 'The selected directory is empty.'
        if err:
            return (None, None, err)
        else:
            return (rawdata, paired_end, err) # a tuple
        # element-wise addition

'''
if file is uploaded lines can be read first then sent to the function:
F=open('groups.tab', 'r')
lines=F.readlines()
F.close()
fun(lines) # a list of lines
'''

# TODO track multiple errors
def read_groups(lines, inputdata):
    # give a list of lines
    samples = {} # dictionaries preserve insertion order
    labels = []
    line_num = 0
    groups = {"rsamps":None, "rgroups":None, "rlabels":None} # default
    err = []

    for line in lines:
        line_num += 1
        parts = [p for p in line.strip().split('\t') if p]
        print(parts)
        if len(parts): # ignore empty lines
            if len(parts) > 3:
                err.append('Line {}: has too many columns, should have exactly 3 columns'.format(line_num))
                continue
                #break
            elif len(parts) < 3:
                err.append('Line {}: has too few columns, should have exactly 3 columns'.format(line_num))
                continue
                #break
            
            # exactly 3 parts
            name = parts[0]
            if name in samples:
                if samples[name] == parts[1:]: # if the other 2 parts match then this line is a duplicate
                    err.append('Line {}: is a duplicate: "{}"'.format(line_num, name))
                continue # do not read in the duplicate group

            if name not in inputdata:
                err.append('Line {}: the sample name {} doesn\'t appear in your data directory'.format(line_num, name))
                continue
                #break

            samples[name] = parts[1:] # group

    if err: # == ''
        return (None, err)
    else:
        groups['rsamps'] = list(samples.keys())
        groups['rgroups'], groups['rlabels'] = list(zip(*samples.values())) # may be multiple groups
#        groups['rlabels']=labels
        return (groups, err)
        # does this dictionary be named exactly this way?

# code to verify groups.tab
# groups.tab must exist, and the groups must exist in groups.tab.
# assuming that a list of groups called groups exists
'''
if file is uploaded then can just read first line
F=open('contrasts.tab', 'r')
line=F.readline() # only need first line
F.close()
'''
def read_contrasts(lines, samples):
    err = []
    contrasts = []
    line_num = 0
    for line in lines:
        line_num += 1
        parts = [p.strip() for p in line.split('\t')]
        if parts in contrasts: # skip duplicates
            continue
        if not len(parts): # skip blank lines
            continue
        if len(parts) > 4:
            err.append('Line {}: needs between 2 to 4 entries'.format(line_num))
            continue
            # break
        elif len(parts) < 2:
            err.append('Line {}: needs between 2 to 4 entries'.format(line_num))
            continue
            # break
        
        if parts[0] in samples and parts[1] in samples:
            while len(parts) < 4:
                parts.append(0.5) # default values when not included
            if isinstance(parts[2], Number) and isinstance(parts[2], Number):
                contrasts.append(parts)
            else:
                err.append('Line {}: columns 3 and 4 should be (small) numbers')
        else:
            s = parts[0] if parts[0] not in samples else parts[1]
            err.append('Line {}: the sample {} doesn\'t exist in samples.tab'.format(line_num, s))
            # break
    #print(contrasts, err)
    return (None, err) if err else (contrasts, err)

# each pair is unique, and the samples exist in the raw data directory. Ignore duplicate lines
def read_pairs(lines, samples):
    err = []
    pairs = []
    tumors = [] # each tumor sample should appear only once
    line_num = 0

    for line in lines:
        line_num += 1
        parts = [p.strip() for p in line.split('\t')]
        if parts in pairs: # skip duplicates
            continue
        if not len(parts): # skip blank lines
            continue
        if len(parts) == 1 or len(parts) > 2:
            err.append('Line {}: needs 2 entries exactly').format(line_num)
            continue
        if parts[0] in samples and parts[1] in samples:
            if parts[1] in tumors:
                err.append('Line {}: tumor "{}" must be unique').format(parts[1])
                continue
            else:
                pairs.append(parts)
        else:
            s = parts[0] if parts[0] not in samples else parts[1]
            err.append('Line {}: the sample {} doesn\'t exist in samples.tab'.format(line_num, s))

    return (None, err) if err else (pairs, err)

# reading peakcall.tab
def read_peaks(lines, samples):
    err = []
    peaks = []
    line_num = 0

    for line in lines:
        line_num += 1
        parts = [p.strip() for p in line.split('\t')]
        if parts in peaks: # skip duplicates
            continue
        if not len(parts): # skip blank lines
            continue
        if len(parts) != 3:
            err.append('Line {}: needs 3 entries exactly').format(line_num)
        else:
            if parts[0] in samples and parts[1] in samples:
                peaks.append(parts)
            else:
                s = parts[0] if parts[0] not in samples else parts[1]
                err.append('Line {}: the sample {} doesn\'t exist in samples.tab'.format(line_num, s))

    return (None, err) if err else (peaks, err)

# reading contrast.tab
def read_contrast_(lines, samples):
    err = []
    contrast_ = []
    line_num = 0

    for line in lines:
        line_num += 1
        parts = [p.strip() for p in line.split('\t')]
        if parts in peaks: # skip duplicates
            continue
        if not len(parts): # skip blank lines
            continue
        if len(parts) != 2:
            err.append('Line {}: needs 2 entries exactly').format(line_num)
        else:
            if parts[0] in samples and parts[1] in samples:
                contrast_.append(parts)
            else:
                s = parts[0] if parts[0] not in samples else parts[1]
                err.append('Line {}: the sample {} doesn\'t exist in samples.tab'.format(line_num, s))

    return (None, err) if err else (contrast_, err)


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
