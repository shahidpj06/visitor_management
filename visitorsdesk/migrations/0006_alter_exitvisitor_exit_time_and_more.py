# Generated by Django 4.2.6 on 2023-12-13 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visitorsdesk', '0005_alter_newvisitor_checkout_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exitvisitor',
            name='exit_time',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='invitevisitor',
            name='checked_out_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='newvisitor',
            name='checkout_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]