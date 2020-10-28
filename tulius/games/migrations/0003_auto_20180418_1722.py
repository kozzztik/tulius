# Generated by Django 2.0.4 on 2018-04-18 14:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('stories', '0001_squashed_0002_auto_20180418_1722'),
        ('games', '0002_auto_20180418_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='rolerequestselection',
            name='role',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='requests',
                to='stories.Role',
                verbose_name='role'),
        ),
        migrations.AddField(
            model_name='gameinvite',
            name='role',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='invites',
                to='stories.Role',
                verbose_name='role'),
        ),
        migrations.AddField(
            model_name='game',
            name='variation',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='games',
                to='stories.Variation',
                verbose_name='variation'),
        ),
        migrations.AlterUniqueTogether(
            name='rolerequestselection',
            unique_together={('role_request', 'role')},
        ),
    ]
