from re import match
from os import walk
from numbers import Number
from werkzeug.utils import secure_filename


def valid_filename(filename):
    '''
    Takes in a filename and determines if it is a valid fastq.gz filename.

    Args:
        filename (str): A filename

    Returns:
        valid (bool): True if the filename is valid, else False
    '''
    rgx = r'^(.+)\.(R[12]\.fastq\.gz)$'
    # err = []
    valid = False
    m = match(rgx, filename)
    if m:
        valid = True
        # err.append('The filename {} should end with R1.fastq.gz or R2.fastq.gz'.format(filename))
        return valid
    else:
        '''
        # filename reporting
        captured = m[1]
        if captured[0].isdigit():
            err.append('Should not start with a digit')
        if ' ' in captured:
            err.append('Should not contain a space')
        if '-' in captured:
            err.append('Should not contain a hyphen/minus sign')
        if 'sample' in captured:
            err.append('Should not contain "sample" before {}'.format(m[2]))
        if 'R1' in captured:
            err.append('Should not contain "R1" before {}'.format(m[2]))
        if 'R2' in captured:
            err.append('Should not contain "R2" before {}'.format(m[2]))
        if len(err):
            err = 'The filename %s has the following errors %s' % filename, err
        '''
        return valid


def read_data_dir(path):
    '''
    Takes a directory and returns valid filenames and other special filenames inside.

    Args:
        path: a directory path

    Returns:
        rawdata (dict of list of str):
            Maps filename prefixes to a list.
            The list contains ints 1 and/or 2 to indicate single/paired-end filenames.
            Note: If errors are present then this value is None.

        paired_end (bool):
            True if paired-end data is found, else False.
            Note: If errors are present then this value is None.

        err (bool):
            True if errors are present, else False.

        specialfound (list of str):
            A list of special filenames present in the directory, as
            specified in the function.
                Note: If errors are present then this value is None.
    '''
    err = ''
    rawdata = {}
    paired_end = False
    count = 0
    rgx = r'^(.*)\.R([12])\.fastq\.gz$'
    specialfiles = ['contrasts.tab', 'contrast.tab',
                    'groups.tab', 'pairs.tab',
                    'peakcall.tab']
    specialfound = []

    # be sure to set limits on .. if needed
    try:
        (_, _, filenames) = next(walk(path))
        for f in filenames:
            if f in specialfiles:
                specialfound.append(f)
            else:
                valid = valid_filename(f)
                if valid:
                    count += 1
                    m = match(rgx, f)
                    print(f)
                    print(m)
                    # m[1] is sample name, m[2] is 1 or 2
                    if m[1] in rawdata:
                        rawdata[m[1]].append(m[2])
                    else:
                        rawdata[m[1]] = [m[2]]

                    if m[2] == '2':
                        paired_end = True

        if not count:  # 0 files found
            err = 'The selected directory "{}" has no relevant fastq files.'.format(path)
    except StopIteration:  # dir doesn't exist
        err = 'The selected directory "{}" does not exist.'.format(path)

    if err:
        return (None, None, err, None)
    else:
        return (rawdata, paired_end, err, specialfound)


def read_groups(lines, prefixes):
    '''
    Takes lines read from groups.tab and file prefixes from the data directory, validates the lines, then returns the file contents as a dict or a list of errors encountered.

    Args:
        lines (list of str):
            Lines from a file, must be groups.tab
        inputdata (list of str):
            File prefixes from the data directory, must pass in read_data_dir output

    Returns:
        groups (dict of list of str):
            Content in lines reorganized by samples, groups, and labels.        Each list is ordered by line number.
            If errors are found, this value is None.
        err (list of str):
            A list of errors
    '''
    samples = {}  # dictionaries preserve insertion order
    labels = []
    line_num = 0
    groups = {'samples': None, 'groups': None, 'labels': None}
    err = []

    for line in lines:
        line_num += 1
        parts = [p for p in line.strip().split('\t') if p]
        if len(parts):  # ignore empty lines
            if len(parts) > 3:
                err.append('Groups.tab, line {}: has too many columns, should have exactly 3 columns'.format(line_num))
                continue
            elif len(parts) < 3:
                err.append('Groups.tab, line {}: has too few columns, should have exactly 3 columns'.format(line_num))
                continue

            # exactly 3 parts
            name = parts[0]
            if name in samples:
                # if the other 2 parts match then this line is a duplicate
                if samples[name] == parts[1:]:
                    err.append('Line {}: is a duplicate: "{}"'.format(line_num, name))
                continue  # do not read in the duplicate group

            if name not in prefixes:
                err.append('Groups.tab, {}: the sample name {} doesn\'t appear in your data directory'.format(line_num, name))
                continue

            samples[name] = parts[1:]  # group

    if err:
        return (None, err)
    else:
        groups['samples'] = list(samples.keys())
        groups['groups'], groups['labels'] = list(zip(*samples.values()))
        return (groups, err)


def read_contrasts(lines, groups):
    '''
    Takes lines read from contrasts.tab and sample names read from groups.tab, validates the lines, then returns the file contents as a list or a list of errors encountered.

    Args:
        lines (list of str):
            Lines from a file, must be contrasts.tab
        groups (list of str):
            Group names from groups.tab, must pass in read_groups output

    Returns:
        contrasts (list of list of str):
            Content in lines as a list format.
            If errors are found, this value is None.
        err (list of str):
            A list of errors
    '''
    err = []
    contrasts = []
    line_num = 0
    for line in lines:
        line_num += 1
        parts = [p for p in line.strip().split('\t') if p]
        if parts in contrasts:  # skip duplicates
            continue
        if not len(parts):  # skip blank lines
            continue
        if len(parts) > 4:
            err.append('Contrasts.tab, line {}: needs between 2 to 4 entries'.format(line_num))
            continue
        elif len(parts) < 2:
            err.append('Contrasts.tab, line {}: needs between 2 to 4 entries'.format(line_num))
            continue

        if parts[0] in groups and parts[1] in groups:
            while len(parts) < 4:
                parts.append(0.5)  # default values when not included
            try:
                parts[2] = float(parts[2])
                parts[3] = float(parts[3])
                contrasts.append(parts)
            except ValueError:
                err.append('Contrasts.tab, line {}: columns 3 and 4 should be (small) numbers'.format(line_num))

        else:
            s = parts[0] if parts[0] not in groups else parts[1]
            err.append('Contrasts.tab, line {}: the sample {} doesn\'t exist in groups.tab'.format(line_num, s))

    return (contrasts, err)


def read_pairs(lines, prefixes):
    '''
    Takes lines read from pairs.tab and file prefixes from the data directory, validates the lines, then returns the file contents as a list or a list of errors encountered.

    Args:
        lines (list of str):
            Lines from a file, must be pairs.tab
        prefixes (list of str):
            File prefixes from the data directory, must pass in read_data_dir output

    Returns:
        contrasts (list of list of str):
            Content in lines as a list format.
            If errors are found, this value is None.
        err (list of str):
            A list of errors
    '''
    err = []
    pairs = []
    tumors = []  # each tumor sample should appear only once
    line_num = 0

    for line in lines:
        line_num += 1
        parts = [p for p in line.strip().split('\t') if p]
        if parts in pairs:  # skip duplicates
            continue
        if not len(parts):  # skip blank lines
            continue
        if len(parts) == 1 or len(parts) > 2:
            err.append('Pairs.tab, line {}: needs 2 entries exactly').format(line_num)
            continue
        if parts[0] in prefixes and parts[1] in prefixes:
            if parts[1] in tumors:
                err.append('Pairs.tab, line {}: tumor "{}" must be unique').format(parts[1])
                continue
            else:
                pairs.append(parts)
        else:
            s = parts[0] if parts[0] not in prefixes else parts[1]
            err.append('Pairs.tab, line {}: the sample name {} doesn\'t appear in your data directory'.format(line_num, s))

    return (pairs, err)


def read_peakcall(lines, prefixes):
    '''
    Takes lines read from peakcall.tab and file prefixes from the data directory, validates the lines, then returns the file contents as a list or a list of errors encountered.

    Args:
        lines (list of str):
            Lines from a file, must be peakcall.tab
        prefixes (list of str):
            File prefixes from the data directory, must pass in read_data_dir output

    Returns:
        peaks (list of list of str):
            Content in lines as a list format.
            If errors are found, this value is None.
        err (list of str):
            A list of errors
    '''
    err = []
    peaks = []
    line_num = 0

    for line in lines:
        line_num += 1
        parts = [p for p in line.strip().split('\t') if p]
        if parts in peaks:  # skip duplicates
            continue
        if not len(parts):  # skip blank lines
            continue
        if len(parts) != 3:
            err.append('Peakcall.tab, line {}: needs 3 entries exactly'.format(line_num))
        else:
            if parts[0] in prefixes and parts[1] in prefixes:
                peaks.append(parts)
            else:
                s = parts[0] if parts[0] not in prefixes else parts[1]
                err.append('Peakcall.tab, line {}: the sample name {} doesn\'t appear in your data directory'.format(line_num, s))

    return (peaks, err)


def read_contrast(lines, groups):
    '''
    Takes lines read from contrast.tab and group names from peakcall.tab, validates the lines, then returns the file contents or a list of errors encountered.

    Args:
        lines (list of str):
            Lines from a file, must be contrast.tab
        groups (list of str):
            Group names from peakcall.tab, must pass in read_peaks output

    Returns:
        contrast (list of list of str):
            Content in lines as a list format.
            If errors are found, this value is None.
        err (list of str):
            A list of errors
    '''
    err = []
    contrast = []
    line_num = 0

    for line in lines:
        line_num += 1
        parts = [p for p in line.strip().split('\t') if p]

        if parts in contrast:  # skip duplicates
            continue

        if not len(parts):  # skip blank lines
            continue

        if len(parts) != 2:
            err.append('Contrast.tab, line {}: needs 2 entries exactly').format(line_num)
        else:
            if parts[0] in groups and parts[1] in groups:
                contrast.append(parts)
            else:
                s = parts[0] if parts[0] not in groups else parts[1]
                err.append('Contrast.tab, line {}: the sample {} doesn\'t exist in peakcall.tab'.format(line_num, s))

    return (contrast, err)


def read_file(file, datatocompare):
    '''
    Takes a file and a set of comparison data, then tries to read the file with the comparison data and return the file contents or a list of errors.

    Args:
        file: the file to read
        datatocompare: the data to be passed as an argument to the appropriate file reading function

    Returns:
        res: The contents of the file as returned by the file reading function, or None if there are errors.
        err: A list of errors generated by the file reading function.

    Raises:
        ValueError: if the filename is not an exact match of special input files.
    '''
    # file must be converted from bytes to string
    name = secure_filename(file.filename)  # strips .. and gets end filename
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
        raise ValueError('No read function for field ' + name)

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
