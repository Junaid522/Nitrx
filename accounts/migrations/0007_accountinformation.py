# Generated by Django 3.1.1 on 2020-10-29 05:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_blockuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountInformation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_valid', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('site_visit', models.BooleanField(default=False)),
                ('partner_info', models.BooleanField(default=False)),
                ('search_privacy', models.BooleanField(default=False)),
                ('store_contacts', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
