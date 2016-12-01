from unittest import TestCase

from mock import MagicMock, Mock, patch
from app.questionnaire.questionnaire_manager import QuestionnaireManager
from app.questionnaire_state.state_item import StateItem
from app.schema.section import Section
from app.schema.skip_condition import SkipCondition
from app.schema.when import When


class TestQuestionnaireManager(TestCase):

    def test_add_answer_creates_new_answer_state(self):
        # Given
        answer_schema = MagicMock()

        question_schema = MagicMock()
        question_schema.answers = [answer_schema]

        self.questionnaire_manager._schema.get_item_by_id = MagicMock(return_value=question_schema)
        self.questionnaire_manager._get_next_answer_instance = MagicMock(return_value=1)

        new_answer_state = MagicMock()
        self.questionnaire_manager._create_new_answer_state = MagicMock(return_value=new_answer_state)

        question_state = MagicMock()
        self.questionnaire_manager.state.find_state_item = MagicMock(return_value=question_state)

        # When
        self.questionnaire_manager.add_answer('block', 'question', self.answer_store)

        # Then
        question_state.create_new_answer_state.assert_called_with(answer_schema, 1)

    def test_add_answer_updates_answer_store(self):
        # Given
        question = MagicMock()
        self.questionnaire_manager.state.find_state_item = MagicMock(return_value=question)
        self.questionnaire_manager.update_questionnaire_store = MagicMock()

        # When
        self.questionnaire_manager.add_answer('block', 'question', self.answer_store)

        # Then
        self.questionnaire_manager.update_questionnaire_store.assert_called_with('block')

    def test_remove_answer_detaches_answer_from_question(self):
        answer_to_remove = self.answers[1]

        with patch.object(self.question, 'remove_answer') as mock:
            self.questionnaire_manager.remove_answer('block', self.answer_store, 1)
            mock.assert_called_with(answer_to_remove)

    def test_remove_answer_removes_from_answer_store(self):
        answer_to_remove = self.answers[1]
        flattened_answer = answer_to_remove.flatten()

        with patch.object(self.answer_store, 'remove') as mock:
            self.questionnaire_manager.remove_answer('block', self.answer_store, 1)
            mock.assert_called_with(flattened_answer)

    def test_get_next_answer_instance_no_previous_answers(self):
        # Given
        qm = self.questionnaire_manager
        answer_store = MagicMock()
        answer_schema = MagicMock()
        answers = []
        answer_store.filter = MagicMock(return_value=answers)

        # When
        next_id = qm._get_next_answer_instance(answer_store, answer_schema)

        # Then
        self.assertEqual(next_id, 0)

    def test_get_next_answer_instance_one_previous_answer(self):
        # Given
        qm = self.questionnaire_manager
        answer_store = MagicMock()
        answer_schema = MagicMock()
        answers = [{'answer_instance': '0'}]
        answer_store.filter = MagicMock(return_value=answers)

        # When
        next_id = qm._get_next_answer_instance(answer_store, answer_schema)

        # Then
        self.assertEqual(next_id, 1)

    def test_get_next_answer_instance_two_previous_answers(self):
        # Given
        qm = self.questionnaire_manager
        answer_store = MagicMock()
        answer_schema = MagicMock()
        answers = [{'answer_instance': '0'}, {'answer_instance': '1'}]
        answer_store.filter = MagicMock(return_value=answers)

        # When
        next_id = qm._get_next_answer_instance(answer_store, answer_schema)

        # Then
        self.assertEqual(next_id, 2)

    def test_get_next_answer_instance_one_more_than_previous_answers(self):
        # Given
        qm = self.questionnaire_manager
        answer_store = MagicMock()
        answer_schema = MagicMock()
        answers = [{'answer_instance': '5'}]
        answer_store.filter = MagicMock(return_value=answers)

        # When
        next_id = qm._get_next_answer_instance(answer_store, answer_schema)

        # Then
        self.assertEqual(next_id, 6)


    def setUp(self):
        # Override some behaviours that are difficult to mock.
        self.original_update_questionnaire_store = QuestionnaireManager.update_questionnaire_store

        QuestionnaireManager.update_questionnaire_store = MagicMock(return_value=None)

        # Class under test.
        self.questionnaire_manager = QuestionnaireManager(MagicMock(), MagicMock())

        # Mock answer store.
        answer_store = MagicMock()
        answer_store.filter = MagicMock(return_value=[])
        self.answer_store = answer_store

        # Mock question.
        self.question = MagicMock()

        # Mock answers.
        answers = []
        for i in range(3):
            answer = MagicMock()
            answer.parent = self.question
            answer.id = i
            answer.flatten = MagicMock(return_value=MagicMock())
            answers.append(answer)

        self.answers = answers
        self.questionnaire_manager.state = MagicMock()
        self.questionnaire_manager.state.get_answers = MagicMock(return_value=self.answers)

    def tearDown(self):
        # Reset some behaviours.
        QuestionnaireManager.update_questionnaire_store = self.original_update_questionnaire_store

    def test_conditional_display_skips_when_equals(self):

        with patch('app.globals.get_answer_store') as get_answer_store:
            answers = {'12345': 'yes'}
            get_answer_store().map = Mock(return_value=answers)

            skip = SkipCondition()
            skip.when = When()

            skip.when.id = '12345'
            skip.when.condition = 'equals'
            skip.when.value = 'yes'

            section = Section()
            section.skip_condition = skip

            state_item = StateItem(id='', schema_item=section)

            self.questionnaire_manager._conditional_display(state_item)

            self.assertEqual(state_item.skipped, True)

    def test_conditional_display_skips_when_not_equals(self):

        with patch('app.globals.get_answer_store') as get_answer_store:
            answers = {'12345': 'yes'}
            get_answer_store().map = Mock(return_value=answers)

            skip = SkipCondition()
            skip.when = When()

            skip.when.id = '12345'
            skip.when.condition = 'not equals'
            skip.when.value = 'no'

            section = Section()
            section.skip_condition = skip

            state_item = StateItem(id='', schema_item=section)

            self.questionnaire_manager._conditional_display(state_item)

            self.assertEqual(state_item.skipped, True)