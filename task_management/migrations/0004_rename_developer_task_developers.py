# Generated by Django 4.1.2 on 2022-10-26 08:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("task_management", "0003_alter_project_manager"),
    ]

    operations = [
        migrations.RenameField(
            model_name="task",
            old_name="developer",
            new_name="developers",
        ),
    ]