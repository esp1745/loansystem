from django.db import models
import random
from django.utils import timezone

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_admin = models.BooleanField('Is admin', default=False)
    is_employee = models.BooleanField('Is employee', default=False)

    # Optional: You can include custom related_name attributes to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True,
    )

  


class ActiveLoans(models.Model):
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('pending_approval', 'Pending Approval'),
    ]
    borrower_name = models.CharField(max_length=100)
    nrc_number = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15)
    collateral_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    principle_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    loan_date = models.DateField()
    loan_due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_approval')
    reference_number = models.CharField(max_length=5, unique=True)
    date_of_loan = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self.generate_unique_reference_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_reference_number():
        while True:
            reference_number = f'{random.randint(10000, 99999)}'
            if not ActiveLoans.objects.filter(reference_number=reference_number).exists():
                return reference_number

class Document(models.Model):
    loan = models.ForeignKey(ActiveLoans, related_name='documents', on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/')

class Payments(models.Model):
    STATUS_CHOICES = [
        ('complete', 'Complete'),
        ('default', 'Default')
    ]

    borrower_name = models.CharField(max_length=255)
    total_loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference_number = models.ForeignKey(ActiveLoans, on_delete=models.CASCADE, to_field='reference_number')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    date_of_payment = models.DateField(default=timezone.now)  # Add this field

    def __str__(self):
        return f'{self.borrower_name} - {self.reference_number}'


class Sales(models.Model):
    collateral_name = models.CharField(max_length=50)
    collateral_amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference_number = models.ForeignKey(ActiveLoans, on_delete=models.CASCADE, to_field='reference_number')
    actual_amount_sold = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    profit_or_loss = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_of_sale = models.DateField(default=timezone.now)

    def __str__(self):
        return f'{self.collateral_name} - {self.reference_number}'


class Expenses(models.Model):
    expense_name = models.CharField(max_length=255)
    expense_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_of_expense = models.DateField(default=timezone.now)

    

class Trackers(models.Model):
    STATUS_CHOICES = [
        ('used', 'Used'),
        ('available', 'Available'),
        ('sold', 'Sold')
    ]

    tracking_number = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=10)
    client_name=models.CharField(max_length=50, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    

    def __str__(self):
        return f'{self.tracking_number}'
