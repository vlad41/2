from datetime import datetime
from os.path import splitext

from django.core.signing import Signer, BadSignature
from django.shortcuts import render
from django.template.loader import render_to_string


# to sign username
ALLOWED_HOSTS = ['*']
PROTOCOL = 'http'
signer = Signer()


def send_activation_notification(user):
    """send activation letter to user
    @:param user - PostUser object
    """
    if ALLOWED_HOSTS:
        host = f'{PROTOCOL}://' + ALLOWED_HOSTS[0]
    else:
        host = f'{PROTOCOL}:localhost:8000'
    context = {'user': user, 'host': host,
               'sign': signer.sign(user.username)}
    subject = render_to_string('email/activation_letter_subject.txt', context)
    body_text = render_to_string('email/activation_letter_body.txt', context)

    user.email_user(subject, body_text)


def get_timestamp_path(instance, filename):
    """convert image name + datetime to filename"""
    return '{}{}'.format(datetime.now().timestamp(), splitext(filename)[1])
