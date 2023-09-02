from django.urls import reverse
from django_celery_beat.models import PeriodicTask
from rest_framework import status
from rest_framework.test import APITestCase

from secret.models import Secret


class SecretTestCase(APITestCase):

    def setUp(self):
        self.data = {
            "secret_phrase": "jupiter is height today",
            "message": "Hello world!",
            "expiration_time": "0:0:1"
        }

    def test_create_delete_secret(self):
        """
        Test creating and deleting a secret
        """
        # Create a secret
        response = self.client.post(
            reverse('secret:create'),
            data=self.data
        )
        # Check that the secret was created
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        # Check that "create" method return the secret phrase
        self.assertEqual(
            response.json(),
            {"secret_phrase": "jupiter is height today"}
        )
        # Check that a periodic task (deleting the secret after time expiration is reached) was created
        # The periodic task has to have the same name as the hashed secret_phrase in the secret object
        secret = Secret.objects.all()
        task_name = secret[0].secret_phrase
        task = PeriodicTask.objects.filter(name=task_name)
        self.assertTrue(task)
        # Check delete the secret
        response = self.client.delete(
                    reverse('secret:delete', kwargs={'pk': self.data.get('secret_phrase')}),
                )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.json(),
            {"message": "Hello world!"}
        )
        # Check that the periodic task was deleted together with the secret object
        task = PeriodicTask.objects.filter(name=task_name)
        self.assertFalse(task)
