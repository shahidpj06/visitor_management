# Generated by Django 4.2.6 on 2023-12-27 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visitorsdesk', '0003_alter_invitevisitor_visitors_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='checked_in',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
