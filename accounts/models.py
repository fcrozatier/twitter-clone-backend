from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(_("email address"), blank=False, unique=True, max_length=255)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
