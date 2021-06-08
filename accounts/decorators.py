from graphql_jwt.decorators import user_passes_test

from accounts import exceptions

login_required = user_passes_test(lambda user: user.is_authenticated, exceptions.LoginRequired)
user_verified = user_passes_test(lambda user: user.status.verified, exceptions.NotVerrifiedAccount)
