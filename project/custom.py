from flask_wtf.file import FileField
from wtforms import Field
from wtforms.fields import Label
from wtforms.validators import DataRequired, Optional, ValidationError
from wtforms.widgets import TextInput
from re import search


class NamedFileField(FileField):
    '''
    A file field that checks the name of its uploaded file against an expected title.
    Inspect the class functions for more details.
    '''
    def __init__(self, *args, **kwargs):
        '''
        Initializes the NamedFileField by calling super() on the FileField

        Args:
            label (str): if a value is provided, it will be formatted by "label.format(expect)".
            validators (list of validators): optionally add extra validators.
            expect (str): the title of the file to expect. ".tab" extension is not required if "label" is not provided.
            required (bool): whether this field is required or not. Just for convenience.
        '''
        label = kwargs.get('label')
        expect = kwargs.get('expect')
        required = kwargs.get('required')
        if label:
            del kwargs['label']
        if expect:
            del kwargs['expect']
        if required:
            del kwargs['required']
        super(FileField, self).__init__(*args, **kwargs)
        
        if label:
            #self.label = Label(label)
            self.expect = expect
        else:
            label = 'Upload ' + expect + '.tab'
            self.expect = expect + '.tab'

        if required:
            self.validators += (DataRequired(), )
            label += ' (required)'
        else:
            self.validators += (Optional(), )
            label += ' (optional)'

        self.label = Label(self.id, label)
        #1/0


    def validate_filename(form, field):
        '''
        Validates the file inside the field if it matches the label defined in __init__
        '''
        filename = secure_filename(field.data.filename)
        1 / 0
        if filename != self.expect:
            message = 'Filename must match {} exactly'.format(self.expect)
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