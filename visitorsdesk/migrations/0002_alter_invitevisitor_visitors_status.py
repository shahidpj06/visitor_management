# Generated by Django 4.2.6 on 2023-12-27 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visitorsdesk', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitevisitor',
            name='visitors_status',
            field=models.CharField(choices=[('Invited Visitor', 'Invited Visitor'), ('Booked Visitor', 'Booked Visitor')], max_length=25),
        ),
    ]
