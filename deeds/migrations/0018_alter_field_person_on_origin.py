# Generated by Django 2.2.6 on 2019-10-31 14:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('deeds', '0017_alter_origin_relates_names'),
    ]

    operations = [
        migrations.AlterField(
            model_name='origin',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='origin_from', to='deeds.Person'),
        ),
    ]