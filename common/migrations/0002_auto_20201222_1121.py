# Generated by Django 3.1.1 on 2020-12-22 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appname',
            name='type',
            field=models.CharField(choices=[('DEVELOPMENT', 'DEVELOPMENT'), ('PRODUCTION', 'PRODUCTION')], default='DEVELOPMENT', max_length=255),
        ),
    ]
