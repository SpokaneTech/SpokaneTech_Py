# Generated by Django 5.0.1 on 2024-05-09 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0008_tag_event_tags'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ['value']},
        ),
        migrations.AlterModelOptions(
            name='techgroup',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='location',
            field=models.CharField(blank=True, help_text='location where this event is being hosted', max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='name',
            field=models.CharField(max_length=1024),
        ),
        migrations.AlterField(
            model_name='event',
            name='tags',
            field=models.ManyToManyField(blank=True, to='web.tag'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='value',
            field=models.CharField(max_length=1024, unique=True),
        ),
        migrations.AlterField(
            model_name='techgroup',
            name='name',
            field=models.CharField(max_length=1024, unique=True),
        ),
    ]