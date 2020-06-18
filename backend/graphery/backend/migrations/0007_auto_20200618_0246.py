# Generated by Django 3.0.7 on 2020-06-18 02:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_auto_20200618_0119'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='GraphInitialCodeExecResultJson',
            new_name='ExecResultJson',
        ),
        migrations.RenameField(
            model_name='tutorial',
            old_name='category',
            new_name='categories',
        ),
        migrations.AddIndex(
            model_name='graph',
            index=models.Index(fields=['url'], name='backend_gra_url_310160_idx'),
        ),
        migrations.AddIndex(
            model_name='tutorial',
            index=models.Index(fields=['url'], name='backend_tut_url_b279e5_idx'),
        ),
    ]