# Generated by Django 5.0.1 on 2024-09-02 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0013_event_approved_data_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='tech_events/'),
        ),
        migrations.AddField(
            model_name='techgroup',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='techgroups/'),
        ),
    ]
