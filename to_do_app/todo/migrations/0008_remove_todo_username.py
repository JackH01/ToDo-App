# Generated by Django 5.1.6 on 2025-04-03 10:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0007_alter_task_done'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='todo',
            name='username',
        ),
    ]
