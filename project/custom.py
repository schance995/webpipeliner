class NamedFileField(FileField):
    '''
    A file field that checks the name of its uploaded file against an expected title.
    '''
    def __init__(self, label='', validators=None, required=False, **kwargs):
        super(FileField, self).__init__(label, validators, **kwargs)
        self.label = 'Upload ' + label + '.tab'
        if required:
            self.validators.append(DataRequired())
            self.label += ' (required)'
        else:
            self.validators.append(Optional())
            self.label += ' (optional)'
        self.validators.append(check_named_file_field(label+'.tab'))

    def validate_filename(form, field):
        shouldbe_search = search(r' ([a-z]*\.tab)')
        if shouldbe_search:
            shouldbe = shouldbe_search.group(1)
        else:
            raise ValueError('No filename was provided during __init__')
        filename = secure_filename(field.data.filename)
        if filename != shouldbe:
            message = 'Filename must match {} exactly'.format(shouldbe)
            raise ValidationError(message)

class FloatListField(Field):
    widget = TextInput()
    # reads default value from a literal float list and returns a comma-separated string
    def _value(self):
        if self.data:
            return ', '.join(self.data)
        else:
            return ''

    # called at form submission but before validation
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [x.strip() for x in valuelist[0].split(',')]
        else:
            self.data = []

    # inline validator
    def validate_float_list(form, field):
        for x in field.data:
            try:
                float(x)
            except ValueError:
                raise ValidationError('Must be a comma-separated list of decimal numbers')