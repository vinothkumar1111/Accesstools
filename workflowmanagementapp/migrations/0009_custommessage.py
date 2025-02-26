# Generated by Django 5.1.1 on 2024-12-24 11:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_mailbox', '0009_alter_message_eml'),
        ('workflowmanagementapp', '0008_messagesytem_recipient_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('read', models.BooleanField(default=False)),
                ('message', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='django_mailbox.message')),
            ],
        ),
    ]
