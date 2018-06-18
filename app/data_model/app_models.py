import datetime
from marshmallow import Schema, fields, post_load, pre_dump


class QuestionnaireState:
    def __init__(self, user_id, q_state, version, created_at=None, updated_at=None):
        self.user_id = user_id
        self.q_state = q_state
        self.version = version
        self.updated_at = updated_at
        self.created_at = created_at


class EQSession:
    def __init__(self, eq_session_id, user_id, session_data=None, created_at=None, updated_at=None):
        self.eq_session_id = eq_session_id
        self.user_id = user_id
        self.session_data = session_data
        self.updated_at = updated_at
        self.created_at = created_at


class UsedJtiClaim:
    def __init__(self, jti_claim, used_at=None):
        self.jti_claim = jti_claim
        self.used_at = used_at or datetime.datetime.now()


class SubmittedResponse:
    def __init__(self, tx_id, data, valid_until):
        self.tx_id = tx_id
        self.data = data
        self.valid_until = valid_until


# pylint: disable=no-self-use
class Timestamp(fields.Field):
    def _serialize(self, value, attr, obj):
        return int(value.strftime('%s'))

    def _deserialize(self, value, attr, data):
        return datetime.datetime.utcfromtimestamp(value)


class LoadObjectMixin:
    def load_object(self, obj):
        data = {field: getattr(obj, field) for field in self._declared_fields}
        return self.load(data)


class DateTimeSchemaMixin:
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

    @pre_dump
    def set_dates(self, data):
        data.created_at = datetime.datetime.now()
        data.updated_at = datetime.datetime.now()
        return data


class QuestionnaireStateSchema(Schema, LoadObjectMixin, DateTimeSchemaMixin):
    user_id = fields.Str()
    q_state = fields.Str()
    version = fields.Integer()

    @post_load
    def make_model(self, data):
        return QuestionnaireState(**data)


class EQSessionSchema(Schema, LoadObjectMixin, DateTimeSchemaMixin):
    eq_session_id = fields.Str()
    user_id = fields.Str()
    session_data = fields.Str()

    @post_load
    def make_model(self, data):
        return EQSession(**data)


class UsedJtiClaimSchema(Schema, LoadObjectMixin):
    jti_claim = fields.Str()
    used_at = fields.DateTime()

    @post_load
    def make_model(self, data):
        return UsedJtiClaim(**data)


class SubmittedResponseSchema(Schema, LoadObjectMixin):
    tx_id = fields.Str()
    data = fields.Str()
    valid_until = Timestamp()

    @post_load
    def make_model(self, data):
        return SubmittedResponse(**data)
