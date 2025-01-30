# workflowmanagementapp/models.py
from django.db import models
from django.contrib.auth.models import User
from tinymce.models import HTMLField
from django.utils.timezone import now, timedelta
from acsapp.models import Project
from django.core.validators import FileExtensionValidator


class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('Loss Of pay', 'Loss Of pay'),
        ('Comp-Off', 'Comp-Off'),
        ('Sick Leave probation', 'Sick Leave probation'),
        ('Optional Holiday', 'Optional Holiday'),
    ]
    
    SESSION_CHOICES = [
        ('Session 1', 'Session 1'),
        ('Session 2', 'Session 2'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Associate leave request with a user
    leave_type = models.CharField(max_length=50, choices=LEAVE_TYPE_CHOICES)
    from_date = models.DateField()
    to_date = models.DateField()
    session_from = models.CharField(max_length=50, choices=SESSION_CHOICES)
    session_to = models.CharField(max_length=50, choices=SESSION_CHOICES)
    reason = models.TextField()
    file = models.FileField(upload_to='leave_attachments/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    current_level = models.IntegerField(default=1)  # 1 = Level1, 2 = Level2, 3 = Level3
    level1_approvers = models.ManyToManyField(User, related_name='level1_leave_requests', blank=True)
    level2_approvers = models.ManyToManyField(User, related_name='level2_leave_requests', blank=True)
    level3_approvers = models.ManyToManyField(User, related_name='level3_leave_requests', blank=True)
    rejection_reason = models.TextField(blank=True, null=True)  # This field will store the rejection reason

    def _str_(self):
        return f"{self.leave_type} from {self.from_date} to {self.to_date} for {self.user.username}"




# class Messagesytem(models.Model):
    
#     sender = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name="sent_messages"
#     )
#     receiver = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name="received_messages", null=True, blank=True
#     )
#     subject = models.CharField(max_length=255, blank=True, null=True)
#     # content = models.TextField()
#     content = HTMLField()  # Use TinyMCE for this field
#     recipient_email = models.EmailField(null=True, blank=True)



#     is_read = models.BooleanField(default=False)
#     created_at = models.DateTimeField(default=now)
#     reply_content = models.TextField(null=True, blank=True)
#     reply_from = models.EmailField(null=True, blank=True)
#     message_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
#     file = models.FileField(
#         upload_to="message_attachments/",
#         blank=True,
#         null=True,
#         validators=[FileExtensionValidator(allowed_extensions=["pdf", "docx", "jpg", "png", "txt"])],
#     )  # Optional file upload field
#     parent_message = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')


#     def __str__(self):
#         return f"Message from {self.sender.username} to {self.receiver.username}"

#     class Meta:
#         ordering = ['-created_at']  # Show newest messages first


# class Notification(models.Model):
#     recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
#     message = models.ForeignKey('Messagesytem', on_delete=models.CASCADE, related_name="notifications")
#     is_read = models.BooleanField(default=False)
#     is_shown = models.BooleanField(default=False)  # Field to check if notification is shown
#     created_at = models.DateTimeField(default=now)

#     def __str__(self):
#         return f"Notification for {self.recipient.username}"


# from django.db import models
# from django_mailbox.models import Message

# # Optional: you can extend or add more fields to this model as needed.
# class CustomMessage(models.Model):
#     message = models.OneToOneField(Message, on_delete=models.CASCADE, related_name='custom_message')
#     read = models.BooleanField(default=False)
#     original_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')

#     def __str__(self):
#         return f"Message from {self.message.subject}"



class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)  # Allow empty or null content
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    file = models.FileField(upload_to='messageuploads/', blank=True, null=True)  # For file uploads
    is_delivered = models.BooleanField(default=False)  # Single tick when True


    parent_message = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, 
        related_name='repliess', related_query_name='replyess'
    )
    is_individual = models.BooleanField(default=True)  # Add this field

    sent = models.BooleanField(default=False)  # Field to track if the message was sent


    def __str__(self):
        
        return f"Message from {self.sender.username} to {self.receiver.username}"

class MessageReply(models.Model):
    message = models.ForeignKey(Message, related_name='replies', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_replies', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply from {self.sender.username} to message {self.message.id}"
    


# Group model to represent a chat group
class Group(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, related_name='groupss', blank=True)  # Add this line

    def __str__(self):
        return self.name


# GroupMembership model to represent users in a group
class GroupMembership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')  # Prevent adding the same user multiple times to a group

    def __str__(self):
        return f'{self.user.username} in {self.group.name}'


# GroupMessage model to store messages in each group
class GroupMessage(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_individual = models.BooleanField(default=False)  # Add this field
    file = models.FileField(upload_to='group_message_uploads/', blank=True, null=True)  # Add this field
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_read = models.BooleanField(default=False)  # Add this field to track read status



    def __str__(self):
        return f'Message by {self.sender.username} in {self.group.name}'
    
class chatNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The user who will receive the notification
    message = models.ForeignKey(Message, on_delete=models.CASCADE)  # The message related to the notification
    is_read = models.BooleanField(default=False)  # Flag to mark whether the notification has been read
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of when the notification was created

    def __str__(self):
        return f"Notification for {self.user.username} regarding message {self.message.id}"



class chatLoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(default=now)
    logout_time = models.DateTimeField(null=True, blank=True)
    logout_reason = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - Login: {self.login_time}, Logout: {self.logout_time}"

    @staticmethod
    def is_user_online(user):
        # Check if the user has a recent login record without a logout time
        last_record = chatLoginHistory.objects.filter(user=user).last()
        if last_record and not last_record.logout_time:
            return True
        # Alternatively, consider a user online if their last logout was within 5 minutes
        if last_record and last_record.logout_time:
            return (now() - last_record.logout_time) <= timedelta(minutes=5)
        return False


class Event(models.Model):
    topic = models.CharField(max_length=200)  # Topic of the event
    organiser = models.CharField(max_length=200)
    partner=models.CharField(max_length=200,default='none')
    partner_logo=models.URLField(blank=True, null=True) # Organiser's name
    project = models.OneToOneField(Project, null=True, blank=True, on_delete=models.SET_NULL, related_name='meeting')
    event_type = models.CharField(max_length=100)  # Type of the event
    participants = models.CharField(max_length=500) # Participants' details
    location = models.CharField(max_length=300)  # Location of the event
    date = models.DateField(null=True)  # Event date
    starttime = models.TimeField(null=True)
    endtime = models.TimeField(null=True)
    actual_starttime = models.TimeField(null=True)
    actual_endtime = models.TimeField(null=True)
    duration = models.DurationField(null=True)
    actual_duration = models.DurationField(null=True)  # Duration of the event
    agenda = models.JSONField(default=list)
    remark = models.JSONField(default=list)
    link = models.URLField(blank=True, null=True)
    prepared_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='prepared_by')

    def __str__(self):
        return f"{self.topic} organized by {self.organiser}"
 
