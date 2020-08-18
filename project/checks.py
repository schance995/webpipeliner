from re import match
from os import walk
from numbers import Number
from werkzeug.utils import secure_filename

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
    
    err = ''
    rawdata = {}
    paired_end = False
    count = 0
    rgx = '^(.*)\.R([12])\.fastq\.gz$'
    specialfiles = ['contrasts.tab', 'contrast.tab', 'groups.tab', 'pairs.tab', 'peakcall.tab']
    specialfound = []
    
    # get only all (base) filenames to simulate the data directory
    # be sure to set limits on .. if needed
    try:
        (_, _, filenames) = next(walk(path))
        for f in filenames:
            if f in specialfiles: specialfound.append(f)
            else:
                valid, _ = valid_filename(f)
                if valid:
                    count += 1
                    m = match(rgx, f)
                    # m[1] = sample name, m[2] = 1 or 2
                    if m[1] in rawdata: rawdata[m[1]].append(m[2])
                    else: rawdata[m[1]] = [m[2]]

                    if m[2] == '2': paired_end = True

        if not count: # 0 files found
            err = 'The selected directory "{}" has no relevant fastq files.'.format(path)
    except StopIteration: # dir doesn't exist
        err = 'The selected directory "{}" does not exist.'.format(path)

    if err: return (None, None, err, None)
    else: return (rawdata, paired_end, err, specialfound)

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
    groups = {'samples':None, 'groups':None, 'labels':None} # default
    err = []

    for line in lines:
        line_num += 1
        parts = [p for p in line.strip().split('\t') if p]
        if len(parts): # ignore empty lines
            if len(parts) > 3:
                err.append('Groups.tab, line {}: has too many columns, should have exactly 3 columns'.format(line_num))
                continue
                #break
            elif len(parts) < 3:
                err.append('Groups.tab, line {}: has too few columns, should have exactly 3 columns'.format(line_num))
                continue
                #break
            
            # exactly 3 parts
            name = parts[0]
            if name in samples:
                if samples[name] == parts[1:]: # if the other 2 parts match then this line is a duplicate
                    err.append('Line {}: is a duplicate: "{}"'.format(line_num, name))
                continue # do not read in the duplicate group

            if name not in inputdata:
                err.append('Groups.tab, {}: the sample name {} doesn\'t appear in your data directory'.format(line_num, name))
                continue
                #break

            samples[name] = parts[1:] # group

    if err: # == ''
        return (None, err)
    else:
        groups['samples'] = list(samples.keys())
        groups['groups'], groups['labels'] = list(zip(*samples.values())) # may be multiple groups
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
        parts = [p for p in line.strip().split('\t') if p]
        if parts in contrasts: # skip duplicates
            continue
        if not len(parts): # skip blank lines
            continue
        if len(parts) > 4:
            err.append('Contrasts.tab, line {}: needs between 2 to 4 entries'.format(line_num))
            continue
            # break
        elif len(parts) < 2:
            err.append('Contrasts.tab, line {}: needs between 2 to 4 entries'.format(line_num))
            continue
            # break
        
        if parts[0] in samples and parts[1] in samples:
            while len(parts) < 4:
                parts.append(0.5) # default values when not included
            try:
                parts[2] = float(parts[2])
                parts[3] = float(parts[3])
                contrasts.append(parts)
            except ValueError:
                err.append('Contrasts.tab, line {}: columns 3 and 4 should be (small) numbers'.format(line_num))
                
        else:
            s = parts[0] if parts[0] not in samples else parts[1]
            err.append('Contrasts.tab, line {}: the sample {} doesn\'t exist in groups.tab'.format(line_num, s))

    return (contrasts, err)

# each pair is unique, and the samples exist in the raw data directory. Ignore duplicate lines
def read_pairs(lines, samples):
    err = []
    pairs = []
    tumors = [] # each tumor sample should appear only once
    line_num = 0

    for line in lines:
        line_num += 1
        parts = [p for p in line.strip().split('\t') if p]
        if parts in pairs: # skip duplicates
            continue
        if not len(parts): # skip blank lines
            continue
        if len(parts) == 1 or len(parts) > 2:
            err.append('Pairs.tab, line {}: needs 2 entries exactly').format(line_num)
            continue
        if parts[0] in samples and parts[1] in samples:
            if parts[1] in tumors:
                err.append('Pairs.tab, line {}: tumor "{}" must be unique').format(parts[1])
                continue
            else:
                pairs.append(parts)
        else:
            s = parts[0] if parts[0] not in samples else parts[1]
            err.append('Pairs.tab, line {}: the sample name {} doesn\'t appear in your data directory'.format(line_num, s))
    
    return (pairs, err)

# reading peakcall.tab
def read_peakcall(lines, samples):
    err = []
    peaks = []
    line_num = 0

    for line in lines:
        line_num += 1
        parts = [p for p in line.strip().split('\t') if p]
        if parts in peaks: # skip duplicates
            continue
        if not len(parts): # skip blank lines
            continue
        if len(parts) != 3:
            err.append('Peakcall.tab, line {}: needs 3 entries exactly'.format(line_num))
        else:
            if parts[0] in samples and parts[1] in samples:
                peaks.append(parts)
            else:
                s = parts[0] if parts[0] not in samples else parts[1]
                err.append('Peakcall.tab, line {}: the sample name {} doesn\'t appear in your data directory'.format(line_num, s))

    return (peaks, err)

# reading contrast.tab
def read_contrast(lines, samples):
    err = []
    contrast = []
    line_num = 0

    for line in lines:
        line_num += 1
        parts = [p for p in line.strip().split('\t') if p]
        
        if parts in contrast: # skip duplicates
            continue
            
        if not len(parts): # skip blank lines
            continue
            
        if len(parts) != 2:
            err.append('Contrast.tab, line {}: needs 2 entries exactly').format(line_num)
        else:
            if parts[0] in samples and parts[1] in samples:
                contrast.append(parts)
            else:
                s = parts[0] if parts[0] not in samples else parts[1]
                err.append('Contrast.tab, line {}: the sample {} doesn\'t exist in peakcall.tab'.format(line_num, s))

    return (contrast, err)

def read_file(file, datatocompare):
    # file must be converted from bytes to string
    name = secure_filename(file.filename) # strips .. and gets end filename
    lines = file.read().decode('utf-8').split('\n')
    func = None
    if name == 'contrast.tab':
        func = read_contrast
    elif name == 'contrasts.tab':
        func = read_contrasts
    elif name == 'pairs.tab':
        func = read_pairs
    elif name == 'peakcall.tab':
        func = read_peakcall
    elif name == 'groups.tab':
        func = read_groups
    else:
        raise ValueError('No read function for field '+name)
    
    res, err = func(lines, datatocompare)
    if err:
        return (None, err)
    else:
        return (res, err)
        
    
# TESTS
if __name__ == '__main__':
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
