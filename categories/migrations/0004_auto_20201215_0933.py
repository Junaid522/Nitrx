# Generated by Django 3.1.1 on 2020-12-15 09:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0003_category_child'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='child',
        ),
        migrations.AddField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='categories.category'),
        ),
    ]
