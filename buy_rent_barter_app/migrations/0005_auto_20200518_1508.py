# Generated by Django 2.1.7 on 2020-05-18 12:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buy_rent_barter_app', '0004_auto_20200518_1503'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proposals',
            options={'ordering': ['-creation_time']},
        ),
    ]