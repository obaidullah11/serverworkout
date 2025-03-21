from django.db import models
from django.utils import timezone
from datetime import timedelta
import pytz


class UserToken(models.Model):
    token = models.CharField(max_length=10, unique=True)
    user_name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    assigned_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.token} - {self.user_name}"

    @classmethod
    def assign_token(cls, user_name, description):
        last_user = cls.objects.order_by('-assigned_time').first()
        pakistan_time = timezone.now().astimezone(pytz.timezone('Asia/Karachi'))

        if last_user:
            next_time = last_user.assigned_time + timedelta(minutes=2)
        else:
            next_time = pakistan_time + timedelta(minutes=2)  # Assign after 2 minutes if no user exists

        # Ensure next_time is not in the past
        if next_time < pakistan_time:
            next_time = pakistan_time  # Adjust to current time if it's in the past

        token_number = cls.objects.count() + 1
        token = f"TKN-{token_number:04d}"

        new_user = cls.objects.create(
            token=token,
            user_name=user_name,
            description=description,
            assigned_time=next_time
        )

        return new_user
