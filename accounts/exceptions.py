from django.utils.translation import ugettext_lazy as _
from graphql_jwt.exceptions import JSONWebTokenError

LOGIN_REQUIRED_ERROR_MSG = "You must login to continue"
NOT_VERIFIED_ACCOUNT_ERROR_MSG = "You must verify you account to continue"


class NotVerrifiedAccount(JSONWebTokenError):
    default_message = _(NOT_VERIFIED_ACCOUNT_ERROR_MSG)


class LoginRequired(JSONWebTokenError):
    default_message = _(LOGIN_REQUIRED_ERROR_MSG)
