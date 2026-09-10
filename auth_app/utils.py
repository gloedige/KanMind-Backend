"""Sammlung allgemeiner Hilfsfunktionen für das Projekt."""

from rest_framework.authtoken.models import Token


def create_user_object(user_account):
    token, created = Token.objects.get_or_create(user=user_account)
    data = {
        'token': token.key,
        'fullname': user_account.username,
        'email': user_account.email,
        'user_id': user_account.id,
    }
    return data