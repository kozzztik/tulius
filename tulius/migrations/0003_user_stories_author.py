# Generated by Django 2.2.13 on 2020-07-22 10:03

from django.db import migrations, models


def migrate_stories_author(apps, schema_editor):
    StoryAuthor = apps.get_model('stories', 'StoryAuthor')
    User = apps.get_model('tulius', 'User')
    count = 0
    for author in StoryAuthor.objects.all():
        s_count = StoryAuthor.objects.filter(user_id=author.user_id).count()
        count += User.objects.filter(pk=author.user_id).update(
            stories_author=s_count)
    total_count = User.objects.all().count()
    print(f'Updated users {count} of {total_count}')


class Migration(migrations.Migration):

    dependencies = [
        ('tulius', '0002_auto_20200107_1601'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='stories_author',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.RunPython(migrate_stories_author),
    ]
