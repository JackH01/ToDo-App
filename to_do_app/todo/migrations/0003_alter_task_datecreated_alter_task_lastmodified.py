# Generated by Django 5.1.6 on 2025-03-07 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0002_alter_todo_datecreated_alter_todo_lastmodified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='dateCreated',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='lastModified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
