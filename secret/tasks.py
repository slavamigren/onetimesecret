from celery import shared_task
from secret.services import dell_object


@shared_task
def dell_expired_object(pk: str) -> None:
    """
    Deletes expired objects from Secret and related periodic task
    """
    dell_object(pk)
