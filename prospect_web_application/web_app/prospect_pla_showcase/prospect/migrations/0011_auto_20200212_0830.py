# Generated by Django 2.2.10 on 2020-02-12 08:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prospect', '0010_amazondetails'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AmazonDetails',
            new_name='AmazonRunDetails',
        ),
    ]
