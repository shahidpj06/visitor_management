# Generated by Django 4.2.6 on 2023-12-26 05:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25, null=True)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('branch_code', models.CharField(max_length=4, null=True)),
                ('counter', models.PositiveIntegerField(default=1, null=True)),
                ('country_code', models.CharField(max_length=25, null=True)),
                ('country_timezone', models.CharField(max_length=50)),
                ('auth_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='branches', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('user_profile', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Desk',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desk_name', models.CharField(max_length=25)),
                ('auth_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='visitorsdesk.company')),
                ('select_branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='add_desk', to='visitorsdesk.branch')),
            ],
        ),
        migrations.CreateModel(
            name='MainUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=25, null=True)),
                ('last_name', models.CharField(max_length=25, null=True)),
                ('useremail', models.EmailField(max_length=25)),
                ('user_phone', models.CharField(max_length=25, null=True)),
                ('username', models.CharField(max_length=25)),
                ('user_role', models.CharField(choices=[('Company Admin', 'Company Admin'), ('Manager', 'Manager'), ('Staff', 'Staff'), ('Host', 'Host')], max_length=25)),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='profile_images/')),
                ('about', models.TextField(blank=True, null=True)),
                ('auth_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='visitorsdesk.company')),
                ('primary_branch', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_profiles', to='visitorsdesk.branch')),
            ],
            options={
                'unique_together': {('auth_user', 'useremail', 'username')},
            },
        ),
        migrations.CreateModel(
            name='NewVisitor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=25)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=25)),
                ('purpose', models.CharField(max_length=25)),
                ('visitor_id', models.CharField(blank=True, max_length=6, null=True)),
                ('checkout_time', models.DateTimeField(blank=True, null=True)),
                ('checkin_time', models.DateTimeField(auto_now_add=True)),
                ('auth_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='visitorsdesk.company')),
                ('select_branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='branch_new_visitor', to='visitorsdesk.branch')),
                ('select_desk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='desk_new_visitor', to='visitorsdesk.desk')),
                ('user_host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='host_new_visitor', to='visitorsdesk.mainuser')),
            ],
        ),
        migrations.CreateModel(
            name='ExitVisitor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exit_time', models.DateTimeField()),
                ('visitor_remarks', models.TextField()),
                ('visitor_id', models.CharField(blank=True, max_length=25, null=True)),
                ('auth_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='visitorsdesk.company')),
                ('exit_desk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exit_desk', to='visitorsdesk.desk')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visitor_name', models.CharField(max_length=25, null=True)),
                ('visitor_email', models.EmailField(max_length=25, null=True)),
                ('visitor_phone', models.CharField(max_length=25, null=True)),
                ('event_name', models.CharField(max_length=25, null=True)),
                ('starts_at', models.DateTimeField(null=True)),
                ('ends_at', models.DateTimeField(null=True)),
                ('event_description', models.TextField(null=True)),
                ('auth_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='visitorsdesk.company')),
                ('staff', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_host', to='visitorsdesk.mainuser')),
            ],
        ),
        migrations.AddField(
            model_name='branch',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='visitorsdesk.company'),
        ),
        migrations.CreateModel(
            name='InviteVisitor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=25, null=True)),
                ('visitor_email', models.EmailField(max_length=254, null=True)),
                ('from_date', models.DateTimeField(null=True)),
                ('to_date', models.DateTimeField(null=True)),
                ('visitor_phone', models.CharField(max_length=25, null=True)),
                ('visitor_id', models.CharField(max_length=8, unique=True)),
                ('purpose', models.CharField(max_length=25)),
                ('visitors_status', models.CharField(choices=[('Booked Visitor', 'Booked Visitor'), ('Invited Visitor', 'Invited Visitor')], max_length=25)),
                ('checked_in', models.BooleanField(default=False, null=True)),
                ('checked_out_at', models.DateTimeField(blank=True, null=True)),
                ('event_description', models.TextField(blank=True, null=True)),
                ('auth_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='visitorsdesk.company')),
                ('select_branch', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invited_vistor', to='visitorsdesk.branch')),
                ('user_host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hosted_user', to='visitorsdesk.mainuser')),
            ],
            options={
                'unique_together': {('visitor_id', 'select_branch')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='branch',
            unique_together={('auth_user', 'name', 'branch_code')},
        ),
    ]
