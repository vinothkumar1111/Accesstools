# Generated by Django 5.1.1 on 2025-01-08 08:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflowmanagementapp', '0023_message_is_delivered'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='members',
        ),
    ]
