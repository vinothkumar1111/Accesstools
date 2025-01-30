# your_app/management/commands/poll_emails.py

from django.core.management.base import BaseCommand
from django_mailbox.models import Mailbox, Message
from plyer import notification  # Library for cross-platform notifications

class Command(BaseCommand):
    print("class")
    help = 'Poll emails from the inbox'

    def handle(self, *args, **options):
        # Get the mailbox that is configured (e.g., 'gmail')
        mailbox = Mailbox.objects.get(name='gmail')

        # Poll for new messages (replies)
        mailbox.poll_for_new_messages()

        # Retrieve any new messages
        new_messages = Message.objects.filter(mailbox=mailbox, read=False).order_by('-received_at')

        for message in new_messages:
            print("poll")
            if message.in_reply_to:  # Check if it's a reply
                # Send a Windows notification for the new reply
                notification.notify(
                    title=f"New Reply: {message.subject}",
                    message=f"You have a new reply from {message.sender}",
                    timeout=10  # Display the notification for 10 seconds
                )

                # Mark the message as read (or you could leave this for later)
                message.read = True
                message.save()

        # Inform the user
        self.stdout.write(self.style.SUCCESS('Successfully polled for new emails'))
