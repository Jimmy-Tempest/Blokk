# Generated by Django 3.2.11 on 2022-01-08 07:24

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='pfp',
            field=models.ImageField(blank=True, null=True, upload_to=api.models.pfp_path),
        ),
    ]
