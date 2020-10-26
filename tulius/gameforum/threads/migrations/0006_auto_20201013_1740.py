# Generated by Django 3.1.1 on 2020-10-13 14:40

from django.db import migrations, models


def migrate_data(apps, schema_editor):
    thread_model = apps.get_model('game_forum_threads', 'Thread')
    count = thread_model.objects.all().update(
        tmp1=models.F('role_id'), tmp2=models.F('edit_role_id'),
        tmp3=models.F('variation_id'))
    print(f'Updated {count} threads')


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('game_forum_threads', '0005_auto_20201013_1739'),
    ]

    operations = [
        migrations.RunPython(migrate_data)
    ]
