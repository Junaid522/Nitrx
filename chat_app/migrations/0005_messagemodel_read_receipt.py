# Generated by Django 3.1.1 on 2021-01-30 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat_app', '0004_auto_20210125_0822'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagemodel',
            name='read_receipt',
            field=models.BooleanField(default=True),
        ),
    ]