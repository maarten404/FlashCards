# Generated by Django 2.1.3 on 2019-04-04 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flashcards', '0005_leveluser'),
    ]

    operations = [
        migrations.AddField(
            model_name='leveluser',
            name='topscore_perc_m',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
