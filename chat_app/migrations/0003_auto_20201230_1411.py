# Generated by Django 3.1.1 on 2020-12-30 14:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat_app', '0002_auto_20201230_1348'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='recipient',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='thread_to_user', to='accounts.user', verbose_name='recipient'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='thread',
            name='user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='thread_from_user', to='accounts.user', verbose_name='user'),
            preserve_default=False,
        ),
    ]
