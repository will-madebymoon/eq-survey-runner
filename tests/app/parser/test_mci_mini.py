from app.parser.schema_parser_factory import SchemaParserFactory
from app.parser.abstract_schema_parser import AbstractSchemaParser
from app.model.questionnaire import Questionnaire
from app.model.group import Group
from app.model.block import Block
from app.model.section import Section
from app.model.question import Question
from app.model.response import Response
import os
import json


def test_mci_mini():
    # Load the json file as a dict
    schema_file = open(os.path.join(os.path.dirname(__file__), 'test_schemas/mci-mini.json'))
    schema = schema_file.read()
    schema = json.loads(schema)

    # create a parser
    parser = SchemaParserFactory.create_parser(schema)

    assert isinstance(parser, AbstractSchemaParser)

    questionnaire = parser.parse()

    # Check the parser version
    assert parser.get_parser_version() == '0.0.1'

    # check the questionniare properties
    assert isinstance(questionnaire, Questionnaire)
    assert questionnaire.id == "22"
    assert questionnaire.survey_id == "23"
    assert questionnaire.title == "Monthly Business Survey - Retail Sales Index"
    assert questionnaire.description == "MCI description"
    assert len(questionnaire.groups) == 1
    assert isinstance(questionnaire.groups[0], Group)

    # check the group properties
    group = questionnaire.groups[0]

    assert group.id == "14ba4707-321d-441d-8d21-b8367366e766"
    assert group.title == ""
    assert len(group.blocks) == 1
    assert isinstance(group.blocks[0], Block)

    # check the block properties
    block = group.blocks[0]
    assert block.id == "cd3b74d1-b687-4051-9634-a8f9ce10a27d"
    assert block.title == "Monthly Business Survey"
    assert len(block.sections) == 1
    assert isinstance(block.sections[0], Section)

    # check the section properties
    section = block.sections[0]
    assert section.id == "2cd99c83-186d-493a-a16d-17cb3c8bd302"
    assert section.title == ""
    assert len(section.questions) == 1
    assert isinstance(section.questions[0], Question)

    # check the question properties
    question = section.questions[0]
    assert question.id == "4ba2ec8a-582f-4985-b4ed-20355deba55a"
    assert question.title == "On 12 January 2016 what was the number of employees for the business named above?"
    assert question.description == "An employee is anyone aged 16 years or over that your organisation directly pays from its payroll(s), in return for carrying out a full-time or part-time job or being on a training scheme."
    assert len(question.responses) == 1
    assert isinstance(question.responses[0], Response)

    # Check the response proeprties
    response = question.responses[0]
    assert response.id == "29586b4c-fb0c-4755-b67d-b3cd398cb30a"
    assert response.code == "110"
    assert response.label == "Male employees working more than 30 hours per week?"
    assert response.guidance == "How many men work for your company?"
    assert response.type == "Integer"