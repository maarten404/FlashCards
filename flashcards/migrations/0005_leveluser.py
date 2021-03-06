# Generated by Django 2.1.3 on 2018-11-15 19:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('flashcards', '0004_auto_20181111_1555'),
    ]

    operations = [
        migrations.CreateModel(
            name='LevelUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topscore', models.PositiveSmallIntegerField()),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flashcards.Level')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
