# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import ActiveLoans, User

@shared_task
def send_loan_due_emails():
    today = timezone.now().date()
    seven_days_from_now = today + timedelta(days=7)

    due_loans = ActiveLoans.objects.filter(loan_due_date__lte=seven_days_from_now, loan_due_date__gte=today)
    email_sent_count = 0

    admin_and_staff_users = User.objects.filter(is_admin=True) | User.objects.filter(is_employee=True)

    for loan in due_loans:
        for user in admin_and_staff_users:
            if user.email:
                subject = 'Reminder: Loan Due Date is Approaching'
                message = (
                    f"Dear {user.username},\n\n"
                    f"This is a reminder that the loan with reference number {loan.reference_number} "
                    f"is due on {loan.loan_due_date}. Please ensure that the borrower is notified "
                    f"to make the necessary payment to avoid any late fees.\n\n"
                    f"Thank you,\nBrolliance Loans"
                )
                from_email = 'brolliance.ltd@gmail.com'
                recipient_list = [user.email]

                send_mail(subject, message, from_email, recipient_list)
                email_sent_count += 1

    return f'Successfully sent {email_sent_count} reminder emails for loans due in 7 days.'
