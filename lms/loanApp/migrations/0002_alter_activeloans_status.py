# Generated by Django 5.0.6 on 2024-07-22 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loanApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activeloans',
            name='status',
            field=models.CharField(choices=[('approved', 'Approved'), ('pending_approval', 'Pending Approval')], default='pending_approval', max_length=20),
        ),
    ]
