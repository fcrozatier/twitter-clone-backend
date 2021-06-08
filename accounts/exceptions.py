from django.utils.translation import ugettext_lazy as _
from graphql_jwt.exceptions import JSONWebTokenError


class NotVerrifiedAccount(JSONWebTokenError):
    default_message = _("You're account is not verified")


class LoginRequired(JSONWebTokenError):
    default_message = _("You must be logged in")
