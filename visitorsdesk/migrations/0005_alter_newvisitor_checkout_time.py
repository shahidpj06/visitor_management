# Generated by Django 4.2.6 on 2023-12-13 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visitorsdesk', '0004_alter_invitevisitor_checked_out_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newvisitor',
            name='checkout_time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]