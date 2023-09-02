from django_celery_beat.models import PeriodicTask
from rest_framework import response, status
from rest_framework.generics import CreateAPIView, DestroyAPIView


from secret.models import Secret
from secret.serializers import SecretDeleteSerializer, SecretCreateSerializer
from secret.services import key_gen, decrypt_secret, add_deleting_task


class SecretCreateView(CreateAPIView):
    """
    Create a new secret
    """
    serializer_class = SecretCreateSerializer
    queryset = Secret.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Create a new secret and return secret phrase
        """
        super().create(request, *args, **kwargs)
        return response.Response({"secret_phrase": self.secret_phrase}, status=status.HTTP_201_CREATED)

    def post(self, request, *args, **kwargs):
        """
        Method saves in database encrypted message and secret phrase. Also, you can set expiration
        time (DD:HH:MM) after which encrypted message and secret phrase will be automatically deleted.
        If you don't set expiration time, 7 days will be set. An example of getting data:
        {
        "secret_phrase": "Time is over",
        "message": "Hello! Come to my place for a party!",
        "expiration_time": "15:0:0"
        }
        Method returns secret phrase in case of success
        An example of returning data:
        {
        "secret_phrase": "Time is over"
        }
        """
        self.secret_phrase = request.data['secret_phrase']
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        The method adds a one-off periodic task, which deletes the secret object,
        when expiration time is reached.
        """
        new_secret = serializer.save()
        time = new_secret.expiration_time.split(':')
        add_deleting_task(int(time[0]), int(time[1]), int(time[2]), new_secret.secret_phrase)


class SecretDeleteView(DestroyAPIView):
    serializer_class = SecretDeleteSerializer
    queryset = Secret.objects.all()

    def destroy(self, *args, **kwargs):
        """
        Destroy method additionally deletes related periodic task
        """
        super().destroy(*args, **kwargs)
        periodic_task = PeriodicTask.objects.filter(name=self.kwargs['pk'])
        if periodic_task:
            periodic_task.delete()
        return response.Response({"message": self.message}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """
        Method gets secret phrase, deletes associated data from database and returns decrypted message.
        An example of using:
        /secrets/Time is over/
        An example of returning data:
        {
        "message": "Hello! Come to my place for a party!"
        }
        """
        key = key_gen(kwargs['pk'].encode('utf-8'))
        self.kwargs['pk'] = key_gen(key).decode('utf-8')
        serializer = self.get_serializer(self.get_object())
        encrypted_message = serializer.data.get('message', None)
        self.message = decrypt_secret(encrypted_message, key)
        return super().delete(request, *args, **self.kwargs)
