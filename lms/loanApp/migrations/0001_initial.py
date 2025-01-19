# Generated by Django 5.0.6 on 2024-07-21 18:22

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActiveLoans',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('borrower_name', models.CharField(max_length=100)),
                ('nrc_number', models.CharField(max_length=20)),
                ('phone_number', models.CharField(max_length=15)),
                ('collateral_name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=200)),
                ('principle_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('interest_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_loan_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('loan_date', models.DateField()),
                ('loan_due_date', models.DateField()),
                ('status', models.CharField(choices=[('approved', 'Approved'), ('pending', 'Pending Approval')], max_length=20)),
                ('reference_number', models.CharField(max_length=5, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='documents/')),
                ('loan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='loanApp.activeloans')),
            ],
        ),
        migrations.CreateModel(
            name='Expenses',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expense_name', models.CharField(max_length=255)),
                ('expense_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date_of_expense', models.DateField()),
                ('reference_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loanApp.activeloans', to_field='reference_number')),
            ],
        ),
        migrations.CreateModel(
            name='Payments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('borrower_name', models.CharField(max_length=255)),
                ('total_loan_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('complete', 'Complete'), ('default', 'Default')], max_length=20)),
                ('reference_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loanApp.activeloans', to_field='reference_number')),
            ],
        ),
        migrations.CreateModel(
            name='Sales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collateral_number', models.CharField(max_length=50)),
                ('collateral_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('reference_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loanApp.activeloans', to_field='reference_number')),
            ],
        ),
        migrations.CreateModel(
            name='Trackers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tracking_number', models.CharField(max_length=50, unique=True)),
                ('phone_number', models.CharField(max_length=20)),
                ('status', models.CharField(choices=[('used', 'Used'), ('available', 'Available'), ('sold', 'Sold')], max_length=20)),
                ('reference_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loanApp.activeloans', to_field='reference_number')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_admin', models.BooleanField(default=False, verbose_name='Is admin')),
                ('is_employee', models.BooleanField(default=False, verbose_name='Is employee')),
                ('groups', models.ManyToManyField(blank=True, related_name='custom_user_set', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='custom_user_permissions_set', to='auth.permission')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
