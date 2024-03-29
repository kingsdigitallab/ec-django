# Generated by Django 2.2.6 on 2019-10-26 15:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('deeds', '0007_alter_field_title_on_profession'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='party',
            options={'verbose_name_plural': 'Parties'},
        ),
        migrations.AlterField(
            model_name='deed',
            name='place',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deeds', to='geonames_place.Place'),
        ),
        migrations.AlterField(
            model_name='origin',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='person_origins', to='deeds.Person'),
        ),
        migrations.AlterField(
            model_name='origin',
            name='place',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='place_origins', to='geonames_place.Place'),
        ),
        migrations.AlterField(
            model_name='party',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='party_to', to='deeds.Person'),
        ),
    ]
