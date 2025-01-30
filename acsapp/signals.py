from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .models import LoginHistory,ActionLog
from django.db.models.signals import pre_delete
from django.contrib.auth.models import User  # Replace with your model

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    # print("log user login ")
    # Create a new login history record on login
    LoginHistory.objects.create(user=user, login_time=timezone.now())

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    # print("log_user_logout")
    # Update the logout time of the last login history record
    last_login_record = LoginHistory.objects.filter(user=user).last()
    if last_login_record and not last_login_record.logout_time:
        last_login_record.logout_time = timezone.now()
        last_login_record.save()



@receiver(pre_delete, sender=User)  # Replace `User` with any model you want to track
def log_deletion(sender, instance, using, **kwargs):
    ActionLog.objects.create(
        user=None,  # If logged-in user info is unavailable in signals
        action='DELETE',
        model_name=sender.__name__,
        object_id=instance.pk,
        object_repr=str(instance)
    )
