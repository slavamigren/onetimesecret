import json
from datetime import datetime, timedelta
from django_celery_beat.models import ClockedSchedule
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from django_celery_beat.models import PeriodicTask
from secret.models import Secret


def encrypt(text: bytes, key: bytes) -> bytes:
    """
    Encrypt a byte string
    """
    cipher = Fernet(key)
    encrypted_text = cipher.encrypt(text)
    return encrypted_text


def decrypt(encrypted_text: bytes, key: bytes) -> bytes:
    """
    Decrypt a byte string
    """
    cipher = Fernet(key)
    decrypted_text = cipher.decrypt(encrypted_text)
    return decrypted_text


def key_gen(secret_phrase: bytes) -> bytes:
    """
    Generate a key 32 bite long out of a byte string
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'',
        iterations=390000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(secret_phrase))
    return key


def encrypt_key_and_secret(message: str, secret_phrase: str) -> (str, str):
    """
    Encrypt an original message and a secret phrase
    """
    binary_message = message.encode('utf-8')
    binary_secret_phrase = secret_phrase.encode('utf-8')
    key = key_gen(binary_secret_phrase)
    hashed_binary_key = key_gen(key)
    encripted_binary_message = encrypt(binary_message, key)
    hashed_key = hashed_binary_key.decode('utf-8')
    encrypted_message = encripted_binary_message.decode('utf-8')
    return encrypted_message, hashed_key


def decrypt_secret(message: bytes, key: bytes) -> str:
    """
    Decrypt a message
    """
    return decrypt(message.encode('utf-8'), key).decode('utf-8')


def dell_object(pk: str) -> None:
    """
    Delete object from Secret and related periodic task
    """
    obj = Secret.objects.filter(pk=pk)
    if obj:
        obj.delete()
    task = PeriodicTask.objects.filter(name=pk)
    if task:
        task.delete()


def add_deleting_task(days: int, hours: int, minutes: int, pk: str) -> None:
    """
    Add related with a secret object one-of periodic task to delete the secret object
    when expiration time is reached
    """
    now = datetime.utcnow()
    clocked, _ = ClockedSchedule.objects.get_or_create(
        clocked_time=now + timedelta(days=days, hours=hours, minutes=minutes)
    )
    PeriodicTask.objects.create(
        clocked=clocked,
        name=pk,
        task="secret.tasks.dell_expired_object",
        one_off=True,
        args=json.dumps([pk]),
        start_time=now
    )
