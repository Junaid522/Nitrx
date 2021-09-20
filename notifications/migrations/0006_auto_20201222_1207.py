# Generated by Django 3.1.1 on 2020-12-22 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0005_auto_20201203_0916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('mention_comment', 'Mention Comment'), ('following', 'Following'), ('like_post', 'Like Post'), ('comment_post', 'Comment Post'), ('rate_story', 'Rate Story'), ('rate_post', 'Rate Post'), ('rate_comment', 'Rate Comment'), ('reply_comment', 'Reply Comment'), ('chat_started', 'Chat Started'), ('group_chat_add', 'Group Chat Add')], max_length=250),
        ),
    ]
