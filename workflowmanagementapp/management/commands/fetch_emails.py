from django.core.management.base import BaseCommand
from django_mailbox.models import Mailbox
from django.utils import timezone
from workflowmanagementapp.models import *

class Command(BaseCommand):
    help = "Fetch new emails from Gmail"

    def handle(self, *args, **kwargs):
        # Fetch emails from the Gmail mailbox
        mailbox = Mailbox.objects.get(name="Gmail Inbox")
        mailbox.fetch_mail()  # Fetches the emails

        # Now process incoming emails
        self.process_incoming_emails()

    def process_incoming_emails(self):
        # Fetch processed messages and replied messages
        unprocessed_messages = CustomMessage.objects.filter(read=False)
        processed_messages = CustomMessage.objects.filter(read=True)

        # Output counts for debugging
        print(f"Unprocessed messages count: {unprocessed_messages.count()}")
        print(f"Processed messages count: {processed_messages.count()}")

        if unprocessed_messages.exists():
            for custom_message in unprocessed_messages:
                self.process_message(custom_message)
            self.stdout.write(self.style.SUCCESS(f'Successfully processed {unprocessed_messages.count()} incoming emails'))
        else:
            self.stdout.write(self.style.SUCCESS('No unprocessed messages found'))

    def process_message(self, custom_message):
        try:
            # Ensure valid 'created_at' field
            if not custom_message.message.created_at:
                self.stdout.write(self.style.ERROR(f"Message {custom_message.id} has no valid 'created_at'"))
                return

            # Update missing date_received
            if custom_message.message.date_received is None:
                custom_message.message.date_received = timezone.now()
                custom_message.message.save()

            # Handle replies if this is a reply to another email
            self.handle_reply_to(custom_message)

            # Mark as processed
            custom_message.read = True
            custom_message.save()
            print(f"Message {custom_message.id} processed successfully.")

        except Exception as e:
            print(f"Unexpected error while processing message {custom_message.id}: {e}")
            self.stdout.write(self.style.ERROR(f"Unexpected error processing message {custom_message.id}: {e}"))

    def handle_reply_to(self, custom_message):
        original_email_id = custom_message.message.in_reply_to
        if original_email_id:
            original_message = CustomMessage.objects.filter(message__message_id=original_email_id).first()
            if original_message:
                custom_message.original_message = original_message
                custom_message.save()
                print(f"Message {custom_message.id} added as a reply to {original_message.id}")
