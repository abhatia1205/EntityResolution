# Generated by Django 2.2.6 on 2019-11-16 18:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dataentry', '0004_auto_20191103_0022'),
    ]

    operations = [
        migrations.AddField(
            model_name='entityresolution',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
