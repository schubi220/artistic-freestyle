# Generated by Django 4.2.7 on 2023-12-05 19:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('artistic', '0002_intial_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='judge',
            name='isReady',
            field=models.BooleanField(default=False, verbose_name='Fertig?'),
        ),
    ]