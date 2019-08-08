# Generated by Django 2.2.3 on 2019-07-10 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fileupload', '0002_sound'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sound',
            name='in_night_index',
            field=models.IntegerField(blank=True, default=0, verbose_name='Index in Night'),
        ),
        migrations.AlterField(
            model_name='sound',
            name='night_number',
            field=models.IntegerField(blank=True, default=0, verbose_name='Night Number'),
        ),
        migrations.AlterField(
            model_name='sound',
            name='recording_date_time',
            field=models.DateTimeField(blank=True, verbose_name='Recording Date-Time'),
        ),
    ]
