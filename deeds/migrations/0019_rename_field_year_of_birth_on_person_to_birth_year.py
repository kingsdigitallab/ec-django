# Generated by Django 2.2.6 on 2019-11-01 09:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deeds', '0018_alter_field_person_on_origin'),
    ]

    operations = [
        migrations.RenameField(
            model_name='person',
            old_name='year_of_birth',
            new_name='birth_year',
        ),
    ]
