# Generated by Django 5.0.6 on 2024-07-22 14:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loanApp', '0002_alter_activeloans_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sales',
            old_name='collateral_number',
            new_name='collateral_name',
        ),
    ]
