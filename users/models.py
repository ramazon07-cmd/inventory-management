from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "admin", "Admin"
        WORKER = "worker", "Worker"

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.WORKER
    )

    email = models.EmailField(unique=True)

    username = models.CharField(max_length=255, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.email} ({self.role})"