# Generated by Django 4.0 on 2021-12-29 19:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0004_create_task_model"),
    ]

    operations = [
        migrations.RenameField(
            model_name="project",
            old_name="user",
            new_name="creator",
        ),
        migrations.RenameField(
            model_name="task",
            old_name="user",
            new_name="creator",
        ),
    ]
