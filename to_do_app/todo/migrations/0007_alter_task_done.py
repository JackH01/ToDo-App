# Generated by Django 5.1.6 on 2025-03-11 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0006_task_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='done',
            field=models.BooleanField(default=False),
        ),
    ]
