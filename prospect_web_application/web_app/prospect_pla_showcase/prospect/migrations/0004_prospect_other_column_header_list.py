# Generated by Django 2.2.10 on 2020-02-05 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prospect', '0003_prospect_run_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='prospect',
            name='other_column_header_list',
            field=models.CharField(max_length=300, null=True),
        ),
    ]
