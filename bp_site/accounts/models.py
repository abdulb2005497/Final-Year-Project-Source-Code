from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    magic_word = models.CharField(
        max_length=100,
        blank=True,
        help_text="A secret word used for extra password recovery."
    )

    def __str__(self):
        return f"Profile for {self.user.username}"
