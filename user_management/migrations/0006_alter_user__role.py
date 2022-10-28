# Generated by Django 4.1.2 on 2022-10-26 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_management", "0005_user_groups_user_user_permissions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="_role",
            field=models.SmallIntegerField(
                choices=[(1, "SUPERUSER"), (2, "MANAGER"), (3, "DEVELOPER")],
                default=3,
                help_text="The role of the user.",
                verbose_name="Role",
            ),
        ),
    ]