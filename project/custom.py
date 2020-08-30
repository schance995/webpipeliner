from flask_wtf.file import FileField
from wtforms import Field
from wtforms.fields import Label
from wtforms.validators import InputRequired, Optional, ValidationError
from wtforms.widgets import TextInput
from re import search


class NamedFileField(FileField):
    '''
    A file field that checks the name of its uploaded file against an expected title.
    Inspect the class functions for more details.
    '''
    def __init__(self, label='', validators=None, expect='', required=False, **kwargs):
        '''
        Initializes the NamedFileField by calling super() on the FileField

        Args:
            label (str): if a value is provided, it will be formatted by "label.format(expect)".
            validators (list of validators): optionally add extra validators.
            expect (str): the title of the file to expect. ".tab" extension is not required if "label" is not provided.
            required (bool): whether this field is required or not.
                If label is not provided then additional text indicating the requirement will be added here in the label.
        '''
        if label:
            self.expect = expect

        else:
            labeltxt = 'Upload ' + expect + '.tab'
            self.expect = expect + '.tab'
            if required:
                labeltxt += ' (required)'
            else:
                labeltxt += ' (optional)'

        #self.required = required
        super(FileField, self).__init__(labeltxt, validators, **kwargs)



    def validate_filename(form, field):
        '''
        Validates the file inside the field if it matches the label defined in __init__
        '''
        if field.data:
            filename = secure_filename(field.data.filename)
            raise ValidationError('{}\t{}'.format(filename), self.expect)
            if filename != self.expect:
                message = 'Filename must match {} exactly'.format(self.expect)
                raise ValidationError(message)
        else:
            if self.required:
                raise ValidationError(self.expect + ' upload is required')


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