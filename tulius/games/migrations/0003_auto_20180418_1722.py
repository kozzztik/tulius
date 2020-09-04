# Generated by Django 2.0.4 on 2018-04-18 14:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('stories', '0001_squashed_0002_auto_20180418_1722'),
        ('games', '0002_auto_20180418_1722'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='rolerequest',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='requested_games',
                to=settings.AUTH_USER_MODEL,
                verbose_name='user'),
        ),
        migrations.AddField(
            model_name='requestquestionanswer',
            name='question',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='answers',
                to='games.RequestQuestion',
                verbose_name='answer'),
        ),
        migrations.AddField(
            model_name='requestquestionanswer',
            name='role_request',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='answers',
                to='games.RoleRequest',
                verbose_name='role request'),
        ),
        migrations.AddField(
            model_name='requestquestion',
            name='game',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='request_questions',
                to='games.Game',
                verbose_name='game'),
        ),
        migrations.AddField(
            model_name='gamewinner',
            name='game',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='winners',
                to='games.Game',
                verbose_name='game'),
        ),
        migrations.AddField(
            model_name='gamewinner',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='winned_games',
                to=settings.AUTH_USER_MODEL,
                verbose_name='user'),
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
            model_name='gameinvite',
            name='sender',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='sended_invites',
                to=settings.AUTH_USER_MODEL,
                verbose_name='sender'),
        ),
        migrations.AddField(
            model_name='gameinvite',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='invites',
                to=settings.AUTH_USER_MODEL,
                verbose_name='user'),
        ),
        migrations.AddField(
            model_name='gameguest',
            name='game',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='guests',
                to='games.Game',
                verbose_name='game'),
        ),
        migrations.AddField(
            model_name='gameguest',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='guested_games',
                to=settings.AUTH_USER_MODEL,
                verbose_name='user'),
        ),
        migrations.AddField(
            model_name='gameadmin',
            name='game',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='admins',
                to='games.Game',
                verbose_name='game'),
        ),
        migrations.AddField(
            model_name='gameadmin',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='admined_games',
                to=settings.AUTH_USER_MODEL,
                verbose_name='user'),
        ),
        migrations.AddField(
            model_name='game',
            name='skin',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='games',
                to='games.Skin',
                verbose_name='skin'),
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
        migrations.AlterUniqueTogether(
            name='gameguest',
            unique_together={('game', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='gameadmin',
            unique_together={('game', 'user')},
        ),
    ]
