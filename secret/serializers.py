from rest_framework import serializers

from secret.models import Secret
from secret.services import encrypt_key_and_secret


class SecretDeleteSerializer(serializers.ModelSerializer):
    """
    Serializer to delete a secret
    """
    class Meta:
        model = Secret
        fields = '__all__'


class SecretCreateSerializer(serializers.ModelSerializer):
    """
    Serializer to create a secret
    It hashes a secret phrase, crypt a message and hashes the secret phrase again, then
    save data to a database
    """
    class Meta:
        model = Secret
        fields = '__all__'

    def validate(self, data):
        data['message'], data['secret_phrase'] = encrypt_key_and_secret(
            data['message'],
            data['secret_phrase']
        )
        return data
