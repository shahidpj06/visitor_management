# Generated by Django 4.2.6 on 2023-12-13 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visitorsdesk', '0003_alter_exitvisitor_exit_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitevisitor',
            name='checked_out_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
