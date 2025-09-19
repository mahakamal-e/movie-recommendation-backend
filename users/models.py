import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ["email"]  # username is still the USERNAME_FIELD by default
    def __str__(self):
        return self.username or self.email