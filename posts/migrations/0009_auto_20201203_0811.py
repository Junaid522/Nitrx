# Generated by Django 3.1.1 on 2020-12-03 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_auto_20201203_0810'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postcomment',
            name='child',
            field=models.ManyToManyField(blank=True, null=True, related_name='_postcomment_child_+', to='posts.PostComment'),
        ),
    ]
