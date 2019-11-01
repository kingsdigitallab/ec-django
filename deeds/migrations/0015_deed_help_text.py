# Generated by Django 2.2.6 on 2019-10-30 17:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('deeds', '0014_person_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deed',
            name='date',
            field=models.DateField(help_text='Date of the deed record'),
        ),
        migrations.AlterField(
            model_name='deed',
            name='place',
            field=models.ForeignKey(help_text='Place of the deed record', on_delete=django.db.models.deletion.CASCADE, related_name='deeds', to='geonames_place.Place'),
        ),
    ]
