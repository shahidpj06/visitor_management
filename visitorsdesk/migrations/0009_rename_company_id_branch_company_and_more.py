# Generated by Django 4.2.6 on 2023-12-14 13:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('visitorsdesk', '0008_rename_company_desk_company_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='branch',
            old_name='company_id',
            new_name='company',
        ),
        migrations.RenameField(
            model_name='desk',
            old_name='company_id',
            new_name='company',
        ),
        migrations.RenameField(
            model_name='exitvisitor',
            old_name='company_id',
            new_name='company',
        ),
        migrations.RenameField(
            model_name='invitevisitor',
            old_name='company_id',
            new_name='company',
        ),
        migrations.RenameField(
            model_name='mainuser',
            old_name='company_id',
            new_name='company',
        ),
        migrations.RenameField(
            model_name='newvisitor',
            old_name='company_id',
            new_name='company',
        ),
    ]
