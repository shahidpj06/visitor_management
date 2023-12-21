# Generated by Django 4.2.6 on 2023-12-19 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visitorsdesk', '0011_event'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='event_date',
        ),
        migrations.RemoveField(
            model_name='event',
            name='event_time',
        ),
        migrations.AddField(
            model_name='event',
            name='ends_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='event_description',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='starts_at',
            field=models.DateTimeField(null=True),
        ),
    ]