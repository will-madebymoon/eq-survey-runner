import unittest
from uuid import UUID

from flask import Flask
from flask_babel import Babel

from app.setup import create_app, versioned_url_for
from app.submitter.submitter import LogSubmitter, RabbitMQSubmitter

from tests import test_settings


class TestCreateApp(unittest.TestCase):

    def test_returns_application(self):
        self.assertIsInstance(create_app(test_settings), Flask)

    # Should new relic have direct access to settings?
    # Probably better for create app to have the control
    def test_setups_newrelic(self):
        with unittest.mock.patch('newrelic.agent.initialize') as new_relic:
            config = {'EQ_NEW_RELIC_ENABLED': "True"}
            config.update(test_settings)

            create_app(config)

            self.assertEqual(new_relic.call_count, 1)

    def test_sets_static_url(self):
        self.assertEqual('/s', create_app(test_settings).static_url_path)

    def test_sets_static_folder_that_exists(self):
        self.assertRegex(create_app(test_settings).static_folder, '../static$')

    def test_sets_content_length(self):
        self.assertGreater(create_app(test_settings).config['MAX_CONTENT_LENGTH'], 0)

    def test_enforces_secure_session(self):
        application = create_app(test_settings)
        self.assertTrue(application.secret_key)
        self.assertTrue(application.permanent_session_lifetime)
        self.assertTrue(application.session_interface)
        # All tests run in dev mode which sets SESSION_COOKIE_SECURE to false
        self.assertFalse(application.config['SESSION_COOKIE_SECURE'])

    # localisation may not be used but is currently attached...
    def test_adds_i18n_to_application(self):
        self.assertIsInstance(create_app(test_settings).babel, Babel)  # pylint: disable=no-member

    def test_adds_logging_of_request_ids(self):
        with unittest.mock.patch('app.setup.logger') as logger:
            config = {
                'EQ_DEV_MODE': True,
                'EQ_APPLICATION_VERSION': False
            }
            config.update(test_settings)

            application = create_app(config)

            application.test_client().get('/')
            self.assertEqual(1, logger.new.call_count)
            _, kwargs = logger.new.call_args
            self.assertTrue(UUID(kwargs['request_id'], version=4))


    def test_enforces_secure_headers(self):
        client = create_app(test_settings).test_client()
        headers = client.get('/').headers
        self.assertEqual('no-cache, no-store, must-revalidate', headers['Cache-Control'])
        self.assertEqual('no-cache', headers['Pragma'])
        self.assertEqual('max-age=31536000; includeSubdomains', headers['Strict-Transport-Security'])
        self.assertEqual('DENY', headers['X-Frame-Options'])
        self.assertEqual('1; mode=block', headers['X-Xss-Protection'])
        self.assertEqual('nosniff', headers['X-Content-Type-Options'])


    # Indirectly covered by higher level integration
    # tests, keeping to highlight that create_app is where
    # it happens.
    def test_adds_blueprints(self):
        self.assertGreater(len(create_app(self._setting_overrides).blueprints), 0)

    def test_removes_db_session_on_teardown(self):
        with unittest.mock.patch('app.setup.Database.remove') as remove:
            application = create_app(test_settings)
            application.test_client().get('/')

            self.assertEqual(remove.call_count, 1)

    def test_versioned_url_for_with_version(self):
        config = {
            'EQ_APPLICATION_VERSION': 'abc123',
            'SERVER_NAME': "test"
        }
        config.update(test_settings)

        application = create_app(config)

        with application.app_context():
            self.assertEqual(
                'http://test/s/a.jpg?q=abc123',
                versioned_url_for('static', filename='a.jpg')
            )

    def test_versioned_url_for_without_version(self):
        config = {
            'EQ_APPLICATION_VERSION': False,
            'SERVER_NAME': "test"
        }
        config.update(test_settings)

        application = create_app(config)

        with application.app_context():
            self.assertEqual(
                'http://test/s/a.jpg?q=False',
                versioned_url_for('static', filename='a.jpg')
            )

    def test_versioned_url_for_minimized_assets(self):
        config = {
            'EQ_MINIMIZE_ASSETS': True,
            'EQ_APPLICATION_VERSION': False,
            'SERVER_NAME': "test"
        }
        config.update(test_settings)

        application = create_app(config)

        with application.app_context():
            self.assertEqual(
                'http://test/s/some.min.css?q=False',
                versioned_url_for('static', filename='some.css')
            )

            self.assertEqual(
                'http://test/s/some.min.js?q=False',
                versioned_url_for('static', filename='some.js')
            )

    def test_versioned_url_for_regular_assets(self):
        config = {
            'EQ_MINIMIZE_ASSETS': False,
            'EQ_APPLICATION_VERSION': False,
            'SERVER_NAME': 'test'

        }
        config.update(test_settings)

        application = create_app(config)

        with application.app_context():
            self.assertEqual(
                'http://test/s/some.css?q=False',
                versioned_url_for('static', filename='some.css')
            )

            self.assertEqual(
                'http://test/s/some.js?q=False',
                versioned_url_for('static', filename='some.js')
            )

    def test_adds_rabbit_submitter_to_the_application(self):
        config = {'EQ_RABBITMQ_ENABLED': True}
        config.update(test_settings)

        application = create_app(config)

        self.assertIsInstance(application.eq['submitter'], RabbitMQSubmitter)

    def test_defaults_to_adding_the_log_submitter_to_the_application(self):
        config = {'EQ_RABBITMQ_ENABLED': False}
        config.update(test_settings)
        application = create_app(config)

        self.assertIsInstance(application.eq['submitter'], LogSubmitter)


if __name__ == '__main__':
    unittest.main()
