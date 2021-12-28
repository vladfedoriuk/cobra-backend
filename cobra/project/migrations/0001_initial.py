# Generated by Django 4.0 on 2021-12-27 20:09

from django.db import migrations, models

import cobra.project.managers
import cobra.utils.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("user", "0004_alter_customuser_first_name_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=250)),
                ("slug", models.SlugField(max_length=250)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.SET(cobra.utils.models.get_default_admin),
                        related_name="%(app_label)s_%(class)s_related",
                        related_query_name="%(app_label)s_%(class)s",
                        to="user.customuser",
                    ),
                ),
            ],
            managers=[
                ("objects", cobra.project.managers.ProjectManager()),
            ],
        ),
        migrations.AddConstraint(
            model_name="project",
            constraint=models.UniqueConstraint(
                fields=("slug", "user"), name="slug_and_user_unique_constraint"
            ),
        ),
    ]
