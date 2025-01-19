
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

from django.shortcuts import render, get_object_or_404, redirect
from .models import ActiveLoans, Payments, Sales, Expenses, Trackers, User
from decimal import Decimal
from django.contrib.auth import logout
from datetime import datetime
from django.db.models import Count
from django.db.models import Sum
from django.db.models import Sum, F,Q
from django.utils.timezone import make_aware
import calendar
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from .tasks import send_loan_due_emails
from django.contrib.auth.decorators import login_required
from .forms import ActiveLoansForm, PaymentsForm, SalesForm, ExpensesForm, TrackerForm, TrackerForm, DocumentFormSet, UploadExcelForm


# Create your views here.
@login_required
def index(request):
    pending_loans = ActiveLoans.objects.filter(status='pending_approval')
    active_loans_count = ActiveLoans.objects.count()
    payments_count = Payments.objects.count()
    sales_count = Sales.objects.count()
    expenses_count = Expenses.objects.count()
    initial_pool_cash = 100000  # Example value
    
    current_pool_cash = calculate_pool_cash(initial_pool_cash)
    pending_requests_count = ActiveLoans.objects.filter(status='pending_approval').count()
    
    # Get monthly complete payments count using the loan_date
    complete_payments = Payments.objects.filter(status='complete')
    complete_loan_dates = ActiveLoans.objects.filter(payments__in=complete_payments).annotate(month=TruncMonth('loan_date')).values('month').annotate(count=Count('id')).values('month', 'count')
    
    # Prepare data for the chart
    monthly_complete_payments_data = {
        'months': [data['month'].strftime('%B %Y') for data in complete_loan_dates],
        'counts': [data['count'] for data in complete_loan_dates]
    }
    
    overall_total_loan_amount = ActiveLoans.objects.aggregate(total=Sum('total_loan_amount'))['total'] or 0
    overall_total_loan_amount_completed = complete_payments.aggregate(total=Sum('total_loan_amount'))['total'] or 0

    today = timezone.now().date()
    seven_days_from_now = today + timedelta(days=7)

    # Fetch loans that are due within the next 7 days
    upcoming_loans = ActiveLoans.objects.filter(loan_due_date__lte=seven_days_from_now, loan_due_date__gte=today)

    # Calculate sums for approved active loans, completed payments, expenses, and sales
    total_active_loans = ActiveLoans.objects.filter(status='approved').aggregate(total=Sum('total_loan_amount'))['total'] or 0
    total_payments = Payments.objects.filter(status='complete').aggregate(total=Sum('total_loan_amount'))['total'] or 0
    total_expenses = Expenses.objects.aggregate(total=Sum('expense_amount'))['total'] or 0
    total_sales = Sales.objects.aggregate(total=Sum('actual_amount_sold'))['total'] or 0

    return render(request, 'index.html', {
        'active_loans_count': active_loans_count,
        'payments_count': payments_count,
        'sales_count': sales_count,
        'expenses_count': expenses_count,
        'pending_requests_count': pending_requests_count,
        'monthly_complete_payments_data': monthly_complete_payments_data,
        'overall_total_loan_amount': overall_total_loan_amount,
        'overall_total_loan_amount_completed': overall_total_loan_amount_completed,
        'upcoming_loans': upcoming_loans,
        'total_active_loans': total_active_loans,
        'total_payments': total_payments,
        'total_expenses': total_expenses,
        'total_sales': total_sales,
        'pending_loans': pending_loans,
        'current_pool_cash':current_pool_cash,
    })

    
@login_required
def index_staff(request):
    today = timezone.now().date()
    
    # Query for overdue loans
    overdue_loans = ActiveLoans.objects.filter(
        loan_due_date__lt=today, 
        status='pending_approval'
    )
    active_loans_count = ActiveLoans.objects.count()
    payments_count = Payments.objects.count()
    sales_count = Sales.objects.count()
    expenses_count = Expenses.objects.count()
    pending_requests_count = ActiveLoans.objects.filter(status='pending_approval').count()
    
    # Get monthly complete payments count using the loan_date
    complete_payments = Payments.objects.filter(status='complete')
    complete_loan_dates = ActiveLoans.objects.filter(payments__in=complete_payments).annotate(month=TruncMonth('loan_date')).values('month').annotate(count=Count('id')).values('month', 'count')
    
    # Prepare data for the chart
    monthly_complete_payments_data = {
        'months': [data['month'].strftime('%B %Y') for data in complete_loan_dates],
        'counts': [data['count'] for data in complete_loan_dates]
    }
    
    overall_total_loan_amount = ActiveLoans.objects.aggregate(total=Sum('total_loan_amount'))['total'] or 0
    overall_total_loan_amount_completed = complete_payments.aggregate(total=Sum('total_loan_amount'))['total'] or 0

    today = timezone.now().date()
    seven_days_from_now = today + timedelta(days=7)

    # Fetch loans that are due within the next 7 days
    upcoming_loans = ActiveLoans.objects.filter(loan_due_date__lte=seven_days_from_now, loan_due_date__gte=today)

    # Calculate sums for approved active loans, completed payments, expenses, and sales
    total_active_loans = ActiveLoans.objects.filter(status='approved').aggregate(total=Sum('total_loan_amount'))['total'] or 0
    total_payments = Payments.objects.filter(status='complete').aggregate(total=Sum('total_loan_amount'))['total'] or 0
    total_expenses = Expenses.objects.aggregate(total=Sum('expense_amount'))['total'] or 0
    total_sales = Sales.objects.aggregate(total=Sum('actual_amount_sold'))['total'] or 0

    return render(request, 'index_staff.html', {
        'active_loans_count': active_loans_count,
        'payments_count': payments_count,
        'sales_count': sales_count,
        'expenses_count': expenses_count,
        'pending_requests_count': pending_requests_count,
        'monthly_complete_payments_data': monthly_complete_payments_data,
        'overall_total_loan_amount': overall_total_loan_amount,
        'overall_total_loan_amount_completed': overall_total_loan_amount_completed,
        'upcoming_loans': upcoming_loans,
        'total_active_loans': total_active_loans,
        'total_payments': total_payments,
        'total_expenses': total_expenses,
        'total_sales': total_sales,
        'overdue_loans':overdue_loans,
    })


def completed_loans_chart(request):
    # Get monthly complete payments count using the loan_date
    complete_payments = Payments.objects.filter(status='complete')
    complete_loan_dates = ActiveLoans.objects.filter(payments__in=complete_payments)\
        .annotate(month=TruncMonth('loan_date'))\
        .values('month')\
        .annotate(count=Count('id'))\
        .values('month', 'count')
    
    # Prepare data for the chart
    months = [data['month'].strftime('%B %Y') for data in complete_loan_dates]
    counts = [data['count'] for data in complete_loan_dates]
    
    # Pass the data to the template
    context = {
        'months': months,
        'counts': counts,
    }
    return render(request, 'completed_loans_chart.html', context)


from .forms import SignUpForm, LoginForm
def register(request):
    msg = None
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            print(f"User created: {user}, Admin: {user.is_admin}, Employee: {user.is_employee}")  # Debug statement
            msg = 'User created'
            return redirect('login_view')
        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form, 'msg': msg})



def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            print(f"Authenticated user: {user}")  # Debug statement
            
            if user is not None:
                if user.is_admin:
                    login(request, user)
                    return redirect('index')
                elif user.is_employee:
                    login(request, user)
                    return redirect('index_staff')
                else:
                    msg = 'User does not have required permissions'
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating form'
    return render(request, 'login.html', {'form': form, 'msg': msg})

def logout_view(request):
    logout(request)
    return redirect('login_view') 




from django.http import HttpResponse
from .tasks import send_loan_due_emails

def test_send_loan_due_emails(request):
    result = send_loan_due_emails.delay()
    return HttpResponse(f'Task initiated with result: {result}')



# ActiveLoans Views
@login_required
def active_loans_list(request):
    query = request.GET.get('q')
    if query:
        loans_list = ActiveLoans.objects.filter(reference_number__icontains=query)
    else:
        loans_list = ActiveLoans.objects.all()
    
    paginator = Paginator(loans_list, 10)  # Show 10 loans per page
    page_number = request.GET.get('page')
    loans = paginator.get_page(page_number)
    
    return render(request, 'activeloans.html', {'loans': loans})




from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
def active_loans_detail(request, pk):
    loan = get_object_or_404(ActiveLoans, pk=pk)
    documents = Document.objects.filter(loan=loan)
    
    if request.method == 'POST':
        if request.user.is_admin:  # Check if the user is an admin
            loan.status = 'approved'
            loan.save()
            return redirect('active_loans_list')
        else:
            return HttpResponseForbidden("You are not authorized to perform this action.")

    context = {
        'loan': loan,
        'documents': documents,
        'can_approve': request.user.is_superuser  # Show approve button only if the user is an admin
    }
    return render(request, 'active_loans_detail.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from .models import ActiveLoans, Document
from .forms import ActiveLoansForm, DocumentForm
import datetime

DocumentFormSet = modelformset_factory(Document, form=DocumentForm, extra=1)

def calculate_interest_amount(principle_amount, loan_date, loan_due_date):
    if loan_due_date and loan_date:
        # Calculate the total number of days between loan_date and loan_due_date
        days_diff = (loan_due_date - loan_date).days
        
        # Convert principle_amount to Decimal
        principle_amount = Decimal(principle_amount)
        
        # Determine the number of months and weeks
        months_diff = days_diff // 30
        weeks_diff = days_diff // 7
        
        # Apply interest calculation based on the longest duration first
        if months_diff >= 1:
            # Apply monthly rate
            interest_amount = principle_amount * Decimal('0.28') * months_diff
        elif weeks_diff >= 1:
            # Apply weekly rate
            interest_amount = principle_amount * Decimal('0.07') * weeks_diff
        else:
            # Apply default interest rate for less than a week
            interest_amount = principle_amount * Decimal('0.07')
        
        return interest_amount

    # Default interest calculation if dates are not provided
    return Decimal(principle_amount) * Decimal('0.07')



@login_required
def active_loans_create(request):
    DocumentFormSet = modelformset_factory(Document, form=DocumentForm, extra=1, can_delete=False)
    
    if request.method == 'POST':
        form = ActiveLoansForm(request.POST, user=request.user)
        formset = DocumentFormSet(request.POST, request.FILES, queryset=Document.objects.none())
        
        if form.is_valid() and formset.is_valid():
            loan = form.save(commit=False)
            loan_date = loan.loan_date
            loan_due_date = loan.loan_due_date
            principle_amount = loan.principle_amount
            loan.interest_amount = calculate_interest_amount(principle_amount, loan_date, loan_due_date)
            loan.total_loan_amount = principle_amount + loan.interest_amount
            loan.save()
            
            for document_form in formset:
                if document_form.cleaned_data.get('file'):
                    document = document_form.save(commit=False)
                    document.loan = loan
                    document.save()
            
            return redirect('active_loans_list')
        else:
            print("Form errors:", form.errors)
            print("Formset errors:", formset.errors)
    else:
        form = ActiveLoansForm(user=request.user)
        formset = DocumentFormSet(queryset=Document.objects.none())
    
    return render(request, 'active_loans_form.html', {'form': form, 'formset': formset})

@login_required
@login_required
def active_loans_update(request, pk):
    loan = get_object_or_404(ActiveLoans, pk=pk)
    
    # Define DocumentFormSet but don't use it in the update logic
    DocumentFormSet = modelformset_factory(Document, form=DocumentForm, extra=1, can_delete=False)
    
    if request.method == 'POST':
        form = ActiveLoansForm(request.POST, instance=loan, user=request.user)
        # Initialize formset but don’t include it in validation or save logic
        formset = DocumentFormSet(request.POST, request.FILES, queryset=Document.objects.none())
        
        if form.is_valid() and formset.is_valid():
            loan = form.save(commit=False)
            loan_date = loan.loan_date
            loan_due_date = loan.loan_due_date
            principle_amount = loan.principle_amount
            loan.interest_amount = calculate_interest_amount(principle_amount, loan_date, loan_due_date)
            loan.total_loan_amount = principle_amount + loan.interest_amount
            loan.save()
            
            # Skip handling the formset if not needed for update
            # for document_form in formset:
            #     if document_form.cleaned_data.get('file'):
            #         document = document_form.save(commit=False)
            #         document.loan = loan
            #         document.save()
            
            return redirect('active_loans_list')
        else:
            print("Form errors:", form.errors)
            print("Formset errors:", formset.errors)
    else:
        form = ActiveLoansForm(instance=loan, user=request.user)
        # Initialize formset with an empty queryset
        formset = DocumentFormSet(queryset=Document.objects.none())
    
    return render(request, 'active_loans_form.html', {'form': form, 'formset': formset})




@login_required
def active_loans_delete(request, pk):
    loan = get_object_or_404(ActiveLoans, pk=pk)
    if request.method == 'POST':
        loan.delete()
        return JsonResponse({'status': 'success', 'message': 'Deleted successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# views.py
@login_required
def approve_loan(request, pk):
    loan = get_object_or_404(ActiveLoans, pk=pk)
    if request.user.is_admin:
        loan.status = 'approved'
        loan.save()
    return redirect('active_loans_detail', pk=pk)



# Payments Views
@login_required
def payments_list(request):
    query = request.GET.get('q')
    if query:
        payments = Payments.objects.filter(reference_number__reference_number__icontains=query)
    else:
        payments = Payments.objects.all()
    
    return render(request, 'payments.html', {'payments': payments, 'query': query})
@login_required
def payments_detail(request, pk):
    payment = get_object_or_404(Payments, pk=pk)
    return render(request, 'payments_detail.html', {'payment': payment})

from django.http import JsonResponse
from .models import ActiveLoans

def get_borrower_name(request):
    reference_number = request.GET.get('reference_number')
    if reference_number:
        try:
            loan = ActiveLoans.objects.get(reference_number=reference_number)
            data = {
                'borrower_name': loan.borrower_name,
                'total_loan_amount': loan.total_loan_amount
            }
        except ActiveLoans.DoesNotExist:
            data = {
                'borrower_name': '',
                'total_loan_amount': ''
            }
    else:
        data = {
            'borrower_name': '',
            'total_loan_amount': ''
        }
    return JsonResponse(data)

@login_required
def payments_create(request):
    loans = ActiveLoans.objects.all()
    if request.method == 'POST':
        form = PaymentsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('payments_list')
    else:
        form = PaymentsForm()
    return render(request, 'payments_form.html', {'form': form, 'loans': loans})
@login_required
def payments_update(request, pk):
    payment = get_object_or_404(Payments, pk=pk)
    loans = ActiveLoans.objects.all()
    if request.method == 'POST':
        form = PaymentsForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            return redirect('payments_list')
    else:
        form = PaymentsForm(instance=payment)
    return render(request, 'payments_form.html', {'form': form, 'loans': loans})
@login_required
def payments_delete(request, pk):
    payment = get_object_or_404(Payments, pk=pk)
    if request.method == 'POST':
        payment.delete()
        return JsonResponse({'status': 'success', 'message': 'Deleted successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# Sales Views
@login_required
def sales_list(request):
    query = request.GET.get('q')
    if query:
        sales = Sales.objects.filter(reference_number__reference_number__icontains=query)
    else:
        sales = Sales.objects.all()
    
    return render(request, 'sales.html', {'sales': sales, 'query': query})
@login_required
def sales_detail(request, pk):
    sale = get_object_or_404(Sales, pk=pk)
    return render(request, 'sales_detail.html', {'sale': sale})

from django.http import JsonResponse

def get_collateral_info(request):
    reference_number = request.GET.get('reference_number')
    if reference_number:
        try:
            loan = ActiveLoans.objects.get(reference_number=reference_number)
            data = {
                'collateral_name': loan.collateral_name,
                'collateral_amount': loan.principle_amount  # Adjust if needed
            }
            return JsonResponse(data)
        except ActiveLoans.DoesNotExist:
            return JsonResponse({'error': 'Loan not found'}, status=404)
    return JsonResponse({'error': 'Reference number not provided'}, status=400)

def get_reference_numbers(request):
    q = request.GET.get('q', '')
    loans = ActiveLoans.objects.filter(reference_number__icontains=q).values_list('reference_number', flat=True)
    results = [{'id': loan, 'text': loan} for loan in loans]
    return JsonResponse({'results': results})

@login_required
def sales_create(request):
    if request.method == 'POST':
        form = SalesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sales_list')
    else:
        form = SalesForm()

    return render(request, 'sales_form.html', {'form': form})
@login_required
def sales_update(request, pk):
    sale = get_object_or_404(Sales, pk=pk)
    if request.method == 'POST':
        form = SalesForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            return redirect('sales_list')
    else:
        form = SalesForm(instance=sale)
    
    return render(request, 'sales_form.html', {'form': form})
@login_required
def sales_delete(request, pk):
    sale = get_object_or_404(Sales, pk=pk)
    if request.method == 'POST':
        sale.delete()
        return JsonResponse({'status': 'success', 'message': 'Deleted successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

from django.core.serializers.json import DjangoJSONEncoder
import json
def sales_chart(request):
    sales = Sales.objects.all()
    collateral_names = json.dumps([sale.collateral_name for sale in sales], cls=DjangoJSONEncoder)
    collateral_amounts = json.dumps([sale.collateral_amount for sale in sales], cls=DjangoJSONEncoder)
    actual_amounts_sold = json.dumps([sale.actual_amount_sold for sale in sales], cls=DjangoJSONEncoder)

    context = {
        'collateral_names': collateral_names,
        'collateral_amounts': collateral_amounts,
        'actual_amounts_sold': actual_amounts_sold,
    }
    return render(request, 'sales_chart.html', context)

# Expenses Views
@login_required
def expenses_list(request):
    query = request.GET.get('q')
    if query:
        # Assuming query is in 'YYYY-MM-DD' format
        try:
            expenses = Expenses.objects.filter(date_of_expense__icontains=query)
        except ValueError:
            expenses = Expenses.objects.all()  # Handle invalid date formats gracefully
    else:
        expenses = Expenses.objects.all()
    
    return render(request, 'expenses.html', {'expenses': expenses, 'query': query})

@login_required
def expenses_detail(request, pk):
    expense = get_object_or_404(Expenses, pk=pk)
    return render(request, 'expenses_detail.html', {'expense': expense})
@login_required
def expenses_create(request):
    if request.method == 'POST':
        form = ExpensesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expenses_list')
    else:
        form = ExpensesForm()
    return render(request, 'expenses_form.html', {'form': form})
@login_required
def expenses_update(request, pk):
    expense = get_object_or_404(Expenses, pk=pk)
    if request.method == 'POST':
        form = ExpensesForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expenses_list')
    else:
        form = ExpensesForm(instance=expense)
    return render(request, 'expenses_form.html', {'form': form})
@login_required
def expenses_delete(request, pk):
    expense = get_object_or_404(Expenses, pk=pk)
    if request.method == 'POST':
        expense.delete()
        return JsonResponse({'status': 'success', 'message': 'Deleted successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# Trackers Views
@login_required
def trackers_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        trackers = Trackers.objects.filter(tracking_number__icontains=search_query)
    else:
        trackers = Trackers.objects.all()
    
    return render(request, 'trackers.html', {'trackers': trackers, 'search_query': search_query})
@login_required
def trackers_detail(request, pk):
    tracker = get_object_or_404(Trackers, pk=pk)
    return render(request, 'trackers_detail.html', {'tracker': tracker})
@login_required
def trackers_create(request):
    if request.method == 'POST':
        form = TrackerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('trackers_list')
    else:
        form = TrackerForm()
    return render(request, 'trackers_form.html', {'form': form})
@login_required
def trackers_update(request, pk):
    tracker = get_object_or_404(Trackers, pk=pk)
    if request.method == 'POST':
        form = TrackerForm(request.POST, instance=tracker)
        if form.is_valid():
            form.save()
            return redirect('trackers_list')
    else:
        form = TrackerForm(instance=tracker)
    return render(request, 'trackers_form.html', {'form': form})
@login_required
def trackers_delete(request, pk):
    tracker = get_object_or_404(Trackers, pk=pk)
    if request.method == 'POST':
        tracker.delete()
        return JsonResponse({'status': 'success', 'message': 'Deleted successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



# in views.py
from django.shortcuts import render
from chartjs.views.lines import BaseLineChartView
from .models import ActiveLoans, Payments, Sales, Expenses

# in views.py

from django.http import JsonResponse
from .models import ActiveLoans, Payments, Sales, Expenses

def loan_status_chart(request):
    approved_count = ActiveLoans.objects.filter(status='approved').count()
    pending_approval_count = ActiveLoans.objects.filter(status='pending_approval').count()
    data = {
        'labels': ['Approved', 'Pending Approval'],
        'data': [[approved_count, pending_approval_count]]
    }
    return JsonResponse(data)

def payment_status_chart(request):
    complete_count = Payments.objects.filter(status='complete').count()
    default_count = Payments.objects.filter(status='default').count()
    data = {
        'labels': ['Complete', 'Default'],
        'data': [complete_count, default_count]
    }
    return JsonResponse(data)

def sales_chart(request):
    sales = Sales.objects.all()
    labels = [sale.collateral_name for sale in sales]
    data = [sale.actual_amount_sold or 0 for sale in sales]
    chart_data = {
        'labels': labels,
        'data': [data]
    }
    return JsonResponse(chart_data)

def expenses_chart(request):
    expenses = Expenses.objects.all()
    labels = [expense.expense_name for expense in expenses]
    data = [expense.expense_amount for expense in expenses]
    chart_data = {
        'labels': labels,
        'data': [data]
    }
    return JsonResponse(chart_data)

def reports_view(request):
    return render(request, 'reports.html')

from django.http import JsonResponse
from django.db.models.functions import TruncMonth
from django.db.models import Count
from .models import Payments
from collections import defaultdict
import calendar
from datetime import datetime

def completed_payments_chart(request):
    # Completed payments data
    completed_data = (Payments.objects
                      .filter(status='complete')
                      .annotate(month=TruncMonth('date_of_payment'))
                      .values('month')
                      .annotate(count=Count('id'))
                      .order_by('month'))

    # Default payments data
    default_data = (Payments.objects
                    .filter(status='default')
                    .annotate(month=TruncMonth('date_of_payment'))
                    .values('month')
                    .annotate(count=Count('id'))
                    .order_by('month'))

    current_year = datetime.now().year
    all_months = [datetime(current_year, month, 1).strftime('%b %Y') for month in range(1, 13)]
    completed_counts = {month: 0 for month in all_months}
    default_counts = {month: 0 for month in all_months}

    # Populate completed counts
    for entry in completed_data:
        month_str = entry['month'].strftime('%b %Y')
        completed_counts[month_str] = entry['count']

    # Populate default counts
    for entry in default_data:
        month_str = entry['month'].strftime('%b %Y')
        default_counts[month_str] = entry['count']

    labels = list(completed_counts.keys())
    completed_values = list(completed_counts.values())
    default_values = list(default_counts.values())

    return JsonResponse({
        'months': labels,
        'completed': completed_values,
        'default': default_values,
    })


def active_loans_status_chart(request):
    data = (ActiveLoans.objects
            .annotate(month=TruncMonth('date_of_loan'))
            .values('month')
            .annotate(approved=Count('id', filter=Q(status='approved')),
                      pending=Count('id', filter=Q(status='pending_approval')))
            .order_by('month'))

    current_year = datetime.now().year
    all_months = [datetime(current_year, month, 1).strftime('%b %Y') for month in range(1, 13)]
    month_counts = {month: {'approved': 0, 'pending': 0} for month in all_months}

    for entry in data:
        month_str = entry['month'].strftime('%b %Y')
        month_counts[month_str]['approved'] = entry['approved']
        month_counts[month_str]['pending'] = entry['pending']

    labels = list(month_counts.keys())
    approved_counts = [v['approved'] for v in month_counts.values()]
    pending_counts = [v['pending'] for v in month_counts.values()]

    return JsonResponse({
        'months': labels,
        'approved': approved_counts,
        'pending': pending_counts,
    })



def sales_chart_data(request):
    sales_data = (Sales.objects
                  .values(month=TruncMonth('date_of_sale'))
                  .annotate(
                      total_profit=Sum(F('profit_or_loss'), filter=Q(profit_or_loss__gt=0)),
                      total_loss=Sum(F('profit_or_loss'), filter=Q(profit_or_loss__lt=0))
                  )
                  .order_by('month'))

    # Generate month labels
    months = [calendar.month_name[i['month'].month] + ' ' + str(i['month'].year) for i in sales_data]
    profit_data = [i['total_profit'] or 0 for i in sales_data]
    loss_data = [i['total_loss'] or 0 for i in sales_data]

    return JsonResponse({
        'months': months,
        'profit': profit_data,
        'loss': loss_data,
    })

# Function to calculate the sum of total_loan_amount in ActiveLoans with status 'approved'
def calculate_total_active_loans():
    total_active_loans = ActiveLoans.objects.filter(status='approved').aggregate(total=Sum('total_loan_amount'))['total'] or 0
    return total_active_loans

# Function to calculate the sum of total_loan_amount in Payments with status 'complete'
def calculate_total_payments():
    total_payments = Payments.objects.filter(status='complete').aggregate(total=Sum('total_loan_amount'))['total'] or 0
    return total_payments

# Function to calculate the sum of expense_amount in Expenses
def calculate_total_expenses():
    total_expenses = Expenses.objects.aggregate(total=Sum('expense_amount'))['total'] or 0
    return total_expenses

# Function to calculate the sum of actual_amount_sold in Sales
def calculate_total_sales():
    total_sales = Sales.objects.aggregate(total=Sum('actual_amount_sold'))['total'] or 0
    return total_sales

# Function to handle the full calculation logic
def loan_summary(request):
    total_active_loans = calculate_total_active_loans()
    total_payments = calculate_total_payments()
    total_expenses = calculate_total_expenses()
    total_sales = calculate_total_sales()
    
    # Adjust total_active_loans by deducting payments with matching reference numbers
    payments_with_active_loans = Payments.objects.filter(reference_number__in=ActiveLoans.objects.values('reference_number'))
    for payment in payments_with_active_loans:
        total_active_loans -= payment.total_loan_amount

    adjusted_payments = total_payments - total_expenses + total_sales

    return render(request, 'loan_summary.html', {
        'total_active_loans': total_active_loans,
        'total_payments': total_payments,
        'total_expenses': total_expenses,
        'total_sales': total_sales,
        'adjusted_payments': adjusted_payments,
    })

import pandas as pd
from django.http import HttpResponse
from .models import ActiveLoans

def download_active_loans_excel(request):
    # Fetch all active loans data from the database
    loans = ActiveLoans.objects.all()

    # Create a list of dictionaries from the query set
    loans_data = list(loans.values(
        'borrower_name', 'nrc_number', 'phone_number', 'collateral_name',
        'address', 'principle_amount', 'interest_amount', 'total_loan_amount',
        'loan_date', 'loan_due_date', 'status', 'reference_number', 'date_of_loan'
    ))

    # Convert the data to a DataFrame
    df = pd.DataFrame(loans_data)

    # Convert the DataFrame to an Excel file in memory
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=active_loans.xlsx'
    df.to_excel(response, index=False, engine='openpyxl')

    return response



def upload_loans(request):
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            
            try:
                # Read the Excel file
                df = pd.read_excel(excel_file, engine='openpyxl')

                # Validate columns
                required_columns = [
                    'borrower_name', 'nrc_number', 'phone_number',
                    'collateral_name', 'address', 'principle_amount',
                    'interest_amount', 'total_loan_amount', 'loan_date',
                    'loan_due_date', 'status'
                ]
                if not all(col in df.columns for col in required_columns):
                    messages.error(request, 'Excel file is missing required columns.')
                    return redirect('upload_loans')

                # Process the DataFrame
                for _, row in df.iterrows():
                    # Create a new ActiveLoans object
                    ActiveLoans.objects.create(
                        borrower_name=row['borrower_name'],
                        nrc_number=row['nrc_number'],
                        phone_number=row['phone_number'],
                        collateral_name=row['collateral_name'],
                        address=row['address'],
                        principle_amount=row['principle_amount'],
                        interest_amount=row['interest_amount'],
                        total_loan_amount=row['total_loan_amount'],
                        loan_date=row['loan_date'],
                        loan_due_date=row['loan_due_date'],
                        status=row['status']
                    )
                messages.success(request, 'Loans have been uploaded successfully.')
                return redirect('active_loans_list')

            except Exception as e:
                messages.error(request, f'Error processing file: {e}')
                return redirect('upload_loans')
    else:
        form = UploadExcelForm()

    return render(request, 'upload_loans.html', {'form': form})


def calculate_pool_cash(initial_pool_cash):
    # Total loan amount in Payments adds to the pool cash
    payments_sum = Payments.objects.filter(status='complete').aggregate(Sum('total_loan_amount'))['total_loan_amount__sum'] or 0
    
    # Principal amount in ActiveLoans deducts from the pool cash
    loans_principal_sum = ActiveLoans.objects.aggregate(Sum('principle_amount'))['principle_amount__sum'] or 0
    
    # Actual amount sold in Sales adds to the pool cash
    sales_sum = Sales.objects.aggregate(Sum('actual_amount_sold'))['actual_amount_sold__sum'] or 0
    
    # Expense amount in Expenses deducts from the pool cash
    expenses_sum = Expenses.objects.aggregate(Sum('expense_amount'))['expense_amount__sum'] or 0
    
    # Calculate the current pool cash
    current_pool_cash = (
        initial_pool_cash + payments_sum + sales_sum - loans_principal_sum - expenses_sum
    )
    
    return current_pool_cash