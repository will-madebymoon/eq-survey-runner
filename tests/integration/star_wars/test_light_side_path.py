import unittest
from app import create_app
from tests.integration.create_token import create_token
from app import settings


class TestLightSidePath(unittest.TestCase):
    def setUp(self):
        settings.EQ_SERVER_SIDE_STORAGE = False
        self.application = create_app('development')
        self.client = self.application.test_client()

    def test_light_side_path(self):
        # Get a token
        token = create_token('star_wars', '0')
        resp = self.client.get('/session?token=' + token.decode(), follow_redirects=True)
        self.assertEquals(resp.status_code, 200)

        # We are on the landing page
        content = resp.get_data(True)

        self.assertRegexpMatches(content, '<title>Introduction</title>')
        self.assertRegexpMatches(content, '>Get Started<')
        self.assertRegexpMatches(content, '(?s)Star Wars.*?Star Wars')

        # We proceed to the questionnaire
        post_data = {
            'action[start_questionnaire]': 'Start Questionnaire'
        }
        resp = self.client.post('/questionnaire/introduction', data=post_data, follow_redirects=False)
        self.assertEquals(resp.status_code, 302)

        block_one_url = resp.headers['Location']

        resp = self.client.get(block_one_url, follow_redirects=False)
        self.assertEquals(resp.status_code, 200)

        # We are in the Questionnaire
        content = resp.get_data(True)
        self.assertRegexpMatches(content, 'Star Wars Quiz')
        self.assertRegexpMatches(content, 'May the force be with you young EQ developer')
        self.assertRegexpMatches(content, ">Save &amp; Continue<")

        # We fill in our answers
        form_data = {
            # Start Date
            "6cf5c72a-c1bf-4d0c-af6c-d0f07bc5b65b": "234",
            "92e49d93-cbdc-4bcb-adb2-0e0af6c9a07c" : "40",
            "pre49d93-cbdc-4bcb-adb2-0e0af6c9a07c": "1370",

            "a5dc09e8-36f2-4bf4-97be-c9e6ca8cbe0d": "Elephant",
            "7587eb9b-f24e-4dc0-ac94-66118b896c10" : "Luke, I am your father",

            "6fd644b0-798e-4a58-a393-a438b32fe637-day": "28",
            "6fd644b0-798e-4a58-a393-a438b32fe637-month": "05",
            "6fd644b0-798e-4a58-a393-a438b32fe637-year": "1983",
            # End Date
            "06a6a4b7-6ce4-4687-879d-3443cd8e2ff0-day": "29",
            "06a6a4b7-6ce4-4687-879d-3443cd8e2ff0-month": "05",
            "06a6a4b7-6ce4-4687-879d-3443cd8e2ff0-year": "1983",
            # Total Turnover
            "215015b1-f87c-4740-9fd4-f01f707ef558": "Wookiees don’t place value in material rewards and refused the medal initially",
            # User Action
            "action[save_continue]": "Save &amp; Continue"
        }

        # We submit the form

        resp = self.client.post(block_one_url, data=form_data, follow_redirects=False)
        self.assertEquals(resp.status_code, 302)

        # There are no validation errors
        self.assertRegexpMatches(resp.headers['Location'], r'\/questionnaire\/summary$')

        summary_url = resp.headers['Location']

        resp = self.client.get(summary_url, follow_redirects=False)
        self.assertEquals(resp.status_code, 200)

        # We are on the review answers page
        content = resp.get_data(True)
        self.assertRegexpMatches(content, '<title>Summary</title>')
        self.assertRegexpMatches(content, '>Star Wars</')
        self.assertRegexpMatches(content, '>Your responses<')
        self.assertRegexpMatches(content, '>Please check carefully before submission<')
        self.assertRegexpMatches(content, '>Submit answers<')

        # We submit our answers
        post_data = {
            "action[submit_answers]": "Submit answers"
        }
        resp = self.client.post(summary_url, data=post_data, follow_redirects=False)
        self.assertEquals(resp.status_code, 302)
        self.assertRegexpMatches(resp.headers['Location'], r'\/questionnaire\/thank-you$')
        resp = self.client.get(resp.headers['Location'], follow_redirects=True)
        self.assertEquals(resp.status_code, 200)

        # We are on the thank you page
        content = resp.get_data(True)
        self.assertRegexpMatches(content, '<title>Thank You</title>')
        self.assertRegexpMatches(content, '(?s)Star Wars.*?Star Wars')
        self.assertRegexpMatches(content, '>Successfully Received<')