# Generated by Django 3.0.3 on 2020-04-29 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0007_auto_20200413_1618'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entity',
            name='name',
        ),
        migrations.AddField(
            model_name='entity',
            name='entity_id',
            field=models.IntegerField(default=0),
        ),
    ]