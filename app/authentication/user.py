from flask_login import UserMixin
from app.storage.storage_factory import StorageFactory
import logging

logger = logging.getLogger(__name__)


class User(UserMixin):

    def __init__(self, user_id):
        if user_id:
            self.user_id = user_id
        else:
            raise ValueError("No user_id found in session")

        self.storage = StorageFactory.get_storage_mechanism()

        if self.storage.has_data(self.user_id):
            self.load()
        else:
            self.questionnaire_data = {}
            self.save()

    def get_user_id(self):
        logger.debug("Returning user id %s", self.user_id)
        return self.user_id

    def get_questionnaire_data(self):
        logger.debug("Returning questionnaire data %s", self.questionnaire_data)
        return self.questionnaire_data

    def delete_questionnaire_data(self):
        logger.debug("Deleting questionnaire data for %s", self.questionnaire_data)
        self.questionnaire_data = {}
        self.storage.delete(self.user_id)

    def save(self):
        logger.debug("Saving user data %s for user id %s", self.questionnaire_data, self.user_id)
        self.storage.store(self.user_id, self.questionnaire_data)

    def load(self):
        self.questionnaire_data = self.storage.get(self.user_id)
