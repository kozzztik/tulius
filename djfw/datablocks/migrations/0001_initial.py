# Generated by Django 2.0.4 on 2018-04-18 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataBlock',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID')),
                (
                    'name',
                    models.CharField(
                        max_length=100, verbose_name='name')),
                (
                    'full_text',
                    models.TextField(
                        blank=True,
                        default='',
                        null=True,
                        verbose_name='text')),
                (
                    'urls',
                    models.TextField(
                        blank=True,
                        default='',
                        null=True,
                        verbose_name='URLs')),
                (
                    'exclude_urls',
                    models.TextField(
                        blank=True,
                        default='',
                        null=True,
                        verbose_name='exclude URLs')),
                (
                    'language',
                    models.CharField(
                        blank=True,
                        editable=False,
                        max_length=10,
                        null=True,
                        verbose_name='language')),
            ],
            options={
                'verbose_name': 'data block',
                'verbose_name_plural': 'data blocks',
                'ordering': ['name'],
            },
        ),
    ]
