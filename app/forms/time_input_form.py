from app.forms.custom_integer_field import CustomIntegerField
from app.validation.validators import FormResponseRequired, IntegerCheck, NumberRange, OptionalForm

from wtforms import Form
from wtforms.validators import StopValidation, ValidationError


def get_time_input_form(answer, error_messages):

    if not error_messages:
        time_input_messages = {}
    else:
        time_input_messages = error_messages.copy()

    if answer['mandatory'] is True:
        if 'validation' in answer and 'messages' in answer['validation'] \
                and 'MANDATORY' in answer['validation']['messages']:
            time_input_messages['MANDATORY'] = answer['validation']['messages']['MANDATORY']

    class TimeInputForm(Form):
        def validate(self):
            is_mandatory = answer.get('mandatory', False)

            valid_hours = True
            valid_minutes = True

            if is_mandatory:
                try:
                    form_validator = FormResponseRequired(message=time_input_messages['MANDATORY'])
                    form_validator(self, None)
                except StopValidation as e:
                    self.hours.errors = [e]
                    return False
            else:
                # If it's an optional form, we don't need to validate
                # any further if unpopulated
                try:
                    form_validator = OptionalForm()
                    form_validator(self, None)
                except StopValidation:
                    return True

            if len(self.hours.raw_data) == 1:
                try:
                    valid_hours = self.hours.validate(self)
                except (StopValidation, ValidationError) as e:
                    self.hours.errors = [e]
                    return False

            if len(self.mins.raw_data) == 1 and len(self.hours.errors) == 0:
                try:
                    valid_minutes = self.mins.validate(self)
                except (StopValidation, ValidationError) as e:
                    self.mins.errors = [e]
                    return False

            return valid_hours and valid_minutes

    if 'validation' in answer and 'messages' in answer['validation'] \
            and 'INVALID_TIME_INPUT' in answer['validation']['messages']:
        time_input_messages['INVALID_TIME'] = answer['validation']['messages']['INVALID_TIME_INPUT']

    TimeInputForm.hours = CustomIntegerField(validators=[
        IntegerCheck(time_input_messages['NOT_INTEGER']),
        NumberRange(0, 999, messages=time_input_messages),
    ])

    TimeInputForm.mins = CustomIntegerField(validators=[
        IntegerCheck(time_input_messages['NOT_INTEGER']),
        NumberRange(0, 59, messages=time_input_messages),
    ])

    return TimeInputForm
