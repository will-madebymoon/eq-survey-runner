import logging
import calendar

from app.validation.error_messages import error_messages
from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, DateField, SelectMultipleField, TextAreaField
from wtforms.widgets import TextArea, TextInput, RadioInput, CheckboxInput, ListWidget
from wtforms.widgets.core import Select, HTMLString, html_params
from wtforms import validators


logger = logging.getLogger(__name__)


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class SelectDateWidget(object):

    # http://stackoverflow.com/questions/14643200/how-to-render-datefield-with-3-selects

    FORMAT_CHOICES = {
        '%m': [(x, calendar.month_name[x]) for x in range(1, 13)]
    }

    FORMAT_CLASSES = {
        '%d': 'select_date_day',
        '%m': 'select_date_month',
        '%Y': 'select_date_year'
    }

    def __init__(self):
        super(SelectDateWidget, self).__init__()

    def __call__(self, field, **kwargs):
        field_id = kwargs.pop('id', field.id)
        html = []
        allowed_format = ['%m']

        for date_format in field.format.split():
            id_suffix = date_format.replace('%', '-')
            id_current = field_id + id_suffix

            if date_format in allowed_format:
                choices = self.FORMAT_CHOICES[date_format]

                kwargs['class'] = self.FORMAT_CLASSES[date_format]
                try:
                    del kwargs['placeholder']
                except:
                    pass

                html.append('<select %s>' % html_params(name=field.name, id=id_current, **kwargs))

                if field.data:
                    current_value = int(field.data.strftime(date_format))
                else:
                    current_value = None

                for value, label in choices:
                    selected = (value == current_value)
                    html.append(Select.render_option(value, label, selected))

                html.append('</select>')
            else:
                html.append('<input type="text" value="" %s></input>' % html_params(name=field.name, id=id_current, **kwargs))

            html.append(' ')

        return HTMLString(''.join(html))


def generate_form(block_json, data):
    class QuestionnaireForm(FlaskForm):
        pass

    for section in block_json['sections']:
        for question in section['questions']:
            for answer in question['answers']:
                name = answer['label'] if answer['label'] else question['title']
                setattr(QuestionnaireForm, answer['id'], get_field(answer, name))

    if data:
        data_class = Struct(**data)
        form = QuestionnaireForm(csrf_enabled=False, obj=data_class)
    else:
        form = QuestionnaireForm(csrf_enabled=False)

    return form


def get_field(answer, label):
    field = None

    logger.info("Setting field to %s, %s", label, answer['guidance'])

    if answer['type'] == 'Radio':
        field = SelectField(
            label=label,
            description=answer['guidance'],
            choices=build_choices(answer['options']),
            widget=ListWidget(),
            option_widget=RadioInput()
        )
    if answer['type'] == 'Checkbox':
        field = SelectMultipleField(
            label=label,
            description=answer.guidance,
            choices=build_choices(answer['options']),
            widget=ListWidget(),
            option_widget=CheckboxInput()
        )
    if answer['type'] == 'Date':
        if answer['mandatory'] is True:
            field = DateField(
                label=label,
                description=answer['guidance'],
                widget=SelectDateWidget(),
                validators=[
                    validators.InputRequired(
                        message=error_messages['MANDATORY']
                    )
                ],
                format="%d %m %Y"
            )
        else:
            field = DateField(
                label=label,
                description=answer['guidance'],
                widget=SelectDateWidget(),
                validators=[validators.Optional()],
                format="%d %m %Y"
            )
    if answer['type'] == 'Currency':
        if answer['mandatory'] is True:
            field = IntegerField(
                label=label,
                description=answer['guidance'],
                widget=TextInput(),
                validators=[
                    validators.InputRequired(
                        message=answer['validation']['messages']['MANDATORY'] or error_messages['MANDATORY']
                    )
                ]
            )
        else:
            label = '<span class="label__inner">'+label+'</span>'
            field = IntegerField(
                label=label,
                description=answer['guidance'],
                widget=TextInput(),
                validators=[
                    validators.Optional()
                ]
            )
    if answer['type'] == 'PositiveInteger' or answer['type'] == 'Integer':
        if answer['mandatory'] is True:
            field = IntegerField(
                label=label,
                description=answer['guidance'],
                widget=TextInput(),
                validators=[
                    validators.InputRequired(
                        message=answer['validation']['messages']['MANDATORY'] or error_messages['MANDATORY']
                    )
                ]
            )
        else:
            label = '<span class="label__inner">'+label+'</span>'
            field = IntegerField(
                label=label,
                description=answer['guidance'],
                widget=TextInput(),
                validators=[
                    validators.Optional()
                ]
            )
    if answer['type'] == 'TextArea':
        field = TextAreaField(
            label=label,
            description=answer['guidance'],
            widget=TextArea(),
            validators=[
                validators.Optional()
            ],
            filters=[lambda x: x if x else None]
        )

    if field is None:
        logger.info("Could not find field for answer type %s", answer['type'])

    return field


def build_choices(options):
    choices = []
    for option in options:
        choices.append((option['label'], option['value']))
    return choices
