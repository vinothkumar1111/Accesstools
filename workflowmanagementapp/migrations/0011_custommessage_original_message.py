# Generated by Django 5.1.1 on 2024-12-26 07:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflowmanagementapp', '0010_alter_custommessage_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='custommessage',
            name='original_message',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to='workflowmanagementapp.custommessage'),
        ),
    ]
