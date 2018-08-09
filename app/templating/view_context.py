from flask_wtf import FlaskForm
from app.jinja_filters import format_currency, format_number, format_unit, format_percentage
from app.helpers.form_helper import get_form_for_location
from app.templating.summary_context import build_summary_rendering_context
from app.templating.template_renderer import renderer
from app.templating.utils import get_title_from_titles, get_question_title
from app.questionnaire.rules import get_answer_store_value


def build_view_context(block_type, metadata, schema, answer_store, schema_context, rendered_block, current_location,
                       form):
    variables = None
    if schema.json.get('variables'):
        variables = renderer.render(schema.json.get('variables'), **schema_context)

    if block_type == 'Summary':
        form = form or FlaskForm()
        return build_view_context_for_final_summary(metadata, schema, answer_store, schema_context, block_type,
                                                    variables, form.csrf_token, rendered_block)
    if block_type == 'SectionSummary':
        form = form or FlaskForm()
        return build_view_context_for_section_summary(metadata, schema, answer_store, schema_context, block_type,
                                                      variables, form.csrf_token, current_location.group_id)

    if block_type == 'CalculatedSummary':
        form = form or FlaskForm()
        return build_view_context_for_calculated_summary(metadata, schema, answer_store, schema_context, block_type,
                                                         variables, form.csrf_token, current_location)

    if block_type in ('Question', 'ConfirmationQuestion'):
        form = form or get_form_for_location(schema, rendered_block, current_location, answer_store, metadata)
        return build_view_context_for_question(metadata, schema, answer_store, current_location, variables,
                                               rendered_block, form)

    if block_type in ('Introduction', 'Interstitial', 'Confirmation'):
        form = form or FlaskForm()
        return build_view_context_for_non_question(variables, form.csrf_token, rendered_block)


def build_view_context_for_non_question(variables, csrf_token, rendered_block):
    return {
        'variables': variables,
        'block': rendered_block,
        'csrf_token': csrf_token,
    }


def build_view_context_for_question(metadata, schema, answer_store, current_location, variables, rendered_block, form):  # noqa: C901, E501  pylint: disable=too-complex,line-too-long

    context = {
        'variables': variables,
        'block': rendered_block,
        'csrf_token': form.csrf_token,
        'question_titles': {},
        'form': {
            'errors': form.errors,
            'question_errors': form.question_errors,
            'mapped_errors': form.map_errors(),
            'answer_errors': {},
            'data': {},
            'other_answer': {},
            'fields': {},
        },
    }

    answer_ids = []
    for question in rendered_block.get('questions'):
        if question.get('titles'):
            context['question_titles'][question['id']] = get_title_from_titles(metadata, schema, answer_store,
                                                                               question['titles'],
                                                                               current_location.group_instance)
        for answer in question['answers']:
            if current_location.block_id == 'household-composition':
                for repeated_form in form.household:
                    answer_ids.append(repeated_form.form[answer['id']].id)
            else:
                answer_ids.append(answer['id'])

            if answer['type'] in ('Checkbox', 'MutuallyExclusiveCheckbox', 'Radio'):
                options = answer['options']
                context['form']['other_answer'][answer['id']] = []
                for index in range(len(options)):
                    context['form']['other_answer'][answer['id']].append(form.get_other_answer(answer['id'], index))

    for answer_id in answer_ids:
        context['form']['answer_errors'][answer_id] = form.answer_errors(answer_id)

        if hasattr(form, 'get_data'):
            context['form']['data'][answer_id] = form.get_data(answer_id)

        if answer_id in form:
            context['form']['fields'][answer_id] = form[answer_id]

    if current_location.block_id in ['household-composition']:
        context['form']['household'] = form.household

    return context


def build_view_context_for_final_summary(metadata, schema, answer_store, schema_context,
                                         block_type, variables, csrf_token, rendered_block):
    section_list = renderer.render(schema.json, **schema_context)['sections']

    context = build_view_context_for_summary(schema, section_list, answer_store, metadata,
                                             csrf_token, block_type, variables)

    context['summary'].update({
        'is_view_submission_response_enabled': is_view_submitted_response_enabled(schema.json),
        'collapsible': rendered_block.get('collapsible', False),
    })

    return context


def build_view_context_for_section_summary(metadata, schema, answer_store, schema_context,
                                           block_type, variables, csrf_token, group_id):
    section_id = schema.get_group(group_id)['parent_id']
    section = schema.get_section(section_id)
    section_list = [renderer.render(section, **schema_context)]
    title = section['title']

    context = build_view_context_for_summary(schema, section_list, answer_store, metadata,
                                             csrf_token, block_type, variables)

    context['summary'].update({
        'title': title,
    })
    return context


def build_view_context_for_calculated_summary(metadata, schema, answer_store, schema_context, block_type,
                                              variables, csrf_token, current_location):
    rendered_block = renderer.render(schema.get_block(current_location.block_id), **schema_context)
    section_list = _build_calculated_summary_section_list(schema, rendered_block, current_location.group_id)

    context = build_view_context_for_summary(schema, section_list, answer_store, metadata,
                                             csrf_token, block_type, variables)

    formatted_total = _get_formatted_total(rendered_block, answer_store, current_location.group_instance, schema)
    context['summary'].update({
        'calculated_question': _get_calculated_question(rendered_block['calculation'], answer_store, schema,
                                                        metadata, current_location.group_instance, formatted_total),
        'title': get_question_title(rendered_block, answer_store, schema, metadata,
                                    current_location.group_instance) % dict(total=formatted_total),
    })
    return context


def build_view_context_for_summary(schema, section_list, answer_store, metadata,
                                   csrf_token, block_type, variables):
    summary_rendering_context = build_summary_rendering_context(schema, section_list, answer_store, metadata)

    context = {
        'csrf_token': csrf_token,
        'summary': {
            'groups': summary_rendering_context,
            'answers_are_editable': True,
            'summary_type': block_type,
        },
        'variables': variables,
    }
    return context


def _build_calculated_summary_section_list(schema, rendered_block, group_id):
    blocks = []
    for block in schema.blocks:
        answers_in_block = schema.get_answers_by_id_for_block(block['id'])
        answers_to_calculate = rendered_block['calculation']['answers_to_calculate']

        answer_matches = set(answers_in_block.keys()) & set(answers_to_calculate)
        if answer_matches:
            blocks.append(_remove_unwanted_questions_answers(block, answers_in_block, answer_matches))

    section = {
        'groups': [
            {
                'id': group_id,
                'blocks': blocks,
            },
        ],
    }

    return [section]


def _remove_unwanted_questions_answers(block, answers_in_block, answer_ids_to_keep):
    reduced_block = block.copy()
    questions_to_keep = [
        answer['parent_id'] for answer in answers_in_block.values() if answer['id'] in answer_ids_to_keep
    ]

    questions = []
    for question in reduced_block['questions']:
        if question['id'] in questions_to_keep:
            answers_to_keep = [answer for answer in question['answers'] if answer['id'] in answer_ids_to_keep]
            question['answers'] = answers_to_keep
            questions.append(question)

    reduced_block['questions'] = questions

    return reduced_block


def _get_formatted_total(block, answer_store, group_instance, schema):
    calculated_total = 0
    for answer in block['calculation']['answers_to_calculate']:
        if group_instance > 0 and not schema.answer_is_in_repeating_group(answer):
            group_instance = 0
        calculated_total += get_answer_store_value(answer, answer_store, group_instance) or 0

    answer_json = schema.get_answer(block['calculation']['answers_to_calculate'][0])
    number_type = answer_json['type']
    if number_type == 'Currency':
        formatted_total = format_currency(calculated_total, answer_json['currency'])
    elif number_type == 'Unit':
        formatted_total = format_unit(answer_json['unit'], calculated_total)
    elif number_type == 'Percentage':
        formatted_total = format_percentage(calculated_total)
    else:
        formatted_total = format_number(calculated_total)

    return formatted_total


def _get_calculated_question(calculation, answer_store, schema, metadata, group_instance, formatted_total):
    calculation_title = get_question_title(calculation, answer_store, schema, metadata, group_instance)

    return {
        'title': calculation_title,
        'id': 'calculated-summary-question',
        'answers': [
            {
                'id': 'calculated-summary-answer',
                'value': formatted_total,
            },
        ],
    }


def is_view_submitted_response_enabled(schema):
    view_submitted_response = schema.get('view_submitted_response')
    if view_submitted_response:
        return view_submitted_response['enabled']

    return False
