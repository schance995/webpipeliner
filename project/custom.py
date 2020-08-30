from flask_wtf.file import FileField
from wtforms import Field
from wtforms.fields import Label
from wtforms.validators import InputRequired, Optional, ValidationError
from wtforms.widgets import TextInput
from re import search
from werkzeug.utils import secure_filename


def validate_filename(form, field):
        '''
        Validates the file inside the field if it matches the label defined in __init__
        Does not raise error if field is empty - include Optional() or InputRequired() in the form if needed
        '''
        if field.data:
            filename = secure_filename(field.data.filename)
            #raise ValidationError('{}\t{}'.format(filename, field.expect))
            if filename != field.expect:
                message = 'Filename must match {} exactly'.format(field.expect)
                raise ValidationError(message)


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

        Note:
            Flask WTForm docs suggest putting super().__init__ at the beginning of the function.
            But since there are some built-in modifications to label text and validators, super is put at the end instead.
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

        if not validators:
            validators = []

        if required:
            validators.insert(0, InputRequired())
        else:
            validators.insert(0, Optional())

        validators.append(validate_filename)

        super(FileField, self).__init__(labeltxt, validators, **kwargs)



class FloatListField(Field):
    '''
    A custom field to represent a list of floating point numbers.

    Attributes:
        widget: a text input box that is used to enter the list of numbers.
    '''
    widget = TextInput()


    def _value(self):
        '''
        Reads default value from a literal float list and returns a comma-separated string
        '''
        if self.data:
            return ', '.join(self.data)
        else:
            return ''


    def process_formdata(self, valuelist):
        '''
        Processes the entered data and saves it to self.
        Called at form submission but before validation.
        '''
        if valuelist:
            self.data = [x.strip() for x in valuelist[0].split(',')]
        else:
            self.data = []


    def validate_float_list(form, field):
        '''
        An inline validator to check that the entered data is a float list.

        Raises:
            ValidationError: if the entered data is not a float list.
        '''
        for x in field.data:
            try:
                float(x)
            except ValueError:
                raise ValidationError('Must be a comma-separated list of decimal numbers')