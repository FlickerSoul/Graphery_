# Generated by Django 3.0.8 on 2020-07-31 17:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0008_auto_20200731_0453'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploads',
            name='tutorial_anchor',
            field=models.ForeignKey(default='3e8c3a27-bb56-4dd2-92a1-069c26b533e4', on_delete=django.db.models.deletion.CASCADE, to='backend.Tutorial'),
            preserve_default=False,
        ),
    ]