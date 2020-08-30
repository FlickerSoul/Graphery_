# Generated by Django 3.1 on 2020-08-27 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0017_add_breakpoints_to_rj'),
    ]

    operations = [
        migrations.AlterField(
            model_name='execresultjson',
            name='json',
            field=models.JSONField(),
        ),
        migrations.AlterField(
            model_name='graph',
            name='cyjs',
            field=models.JSONField(),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
    ]
