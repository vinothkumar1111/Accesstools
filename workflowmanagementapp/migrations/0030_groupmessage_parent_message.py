# Generated by Django 5.1.1 on 2025-01-22 09:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflowmanagementapp', '0029_rename_sent_at_groupmessage_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupmessage',
            name='parent_message',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='workflowmanagementapp.groupmessage'),
        ),
    ]
