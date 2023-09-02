from django.core.exceptions import ValidationError
from django.db import models
from re import fullmatch


def validate_expiration(value):
    if not fullmatch(r'\d\d?\d?:\d\d?:\d\d?', value):
        raise ValidationError('Format the string of time deleting: DD:HH:MM')
    elif fullmatch(r'\d\d?\d?:\d\d?:\d\d?', value) and (int(value.split(':')[1]) > 23 or int(value.split(':')[2]) > 59):
        raise ValidationError('Hours or minutes set incorrectly')


class Secret(models.Model):
    secret_phrase = models.CharField(max_length=150, primary_key=True, verbose_name='secret_phrase')
    message = models.TextField(verbose_name='message')
    expiration_time = models.CharField(
        max_length=9,
        default='7:0:0',
        validators=[validate_expiration],
        verbose_name='expiration_time'
    )

    class Meta:
        verbose_name = 'secret'
        verbose_name_plural = 'secrets'
