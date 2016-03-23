# -*- coding: utf-8 -*-

# Third Party Stuff
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model

user_model = get_user_model()


def get_token_for_user(user, scope):
    """
    Generate a new signed token containing
    a specified user limited for a scope (identified as a string).
    """
    data = {
        "user_%s_id" % (scope): str(user.id),
    }
    return jwt.encode(data, settings.SECRET_KEY).decode('utf-8')


def get_user_for_token(token, scope):
    """
    Given a self-contained token and a scope try to parse and
    unsign it.

    If max_age is specified it checks token expiration.

    If token passes a validation, returns
    a user instance corresponding with user_id stored
    in the incoming token.
    """
    try:
        data = jwt.decode(token, settings.SECRET_KEY)
    except jwt.DecodeError:
        return None

    try:
        user = user_model.objects.get(pk=data["user_%s_id" % (scope)])
    except (user_model.DoesNotExist, KeyError):
        return None
    else:
        return user
