# Generated by Django 2.2.10 on 2020-02-06 04:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prospect', '0006_auto_20200205_1243'),
    ]

    operations = [
        migrations.AddField(
            model_name='rundetails',
            name='post_process_completed',
            field=models.BooleanField(default=False),
        ),
    ]
