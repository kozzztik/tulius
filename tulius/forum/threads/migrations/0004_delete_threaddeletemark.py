# Generated by Django 2.2.13 on 2020-07-25 13:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum_threads', '0003_migrate_delete_marks'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ThreadDeleteMark',
        ),
    ]