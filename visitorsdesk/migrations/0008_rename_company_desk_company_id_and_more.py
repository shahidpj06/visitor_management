# Generated by Django 4.2.6 on 2023-12-14 13:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('visitorsdesk', '0007_rename_company_branch_company_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='desk',
            old_name='company',
            new_name='company_id',
        ),
        migrations.RenameField(
            model_name='exitvisitor',
            old_name='company',
            new_name='company_id',
        ),
        migrations.RenameField(
            model_name='invitevisitor',
            old_name='company',
            new_name='company_id',
        ),
        migrations.RenameField(
            model_name='mainuser',
            old_name='company',
            new_name='company_id',
        ),
        migrations.RenameField(
            model_name='newvisitor',
            old_name='company',
            new_name='company_id',
        ),
    ]