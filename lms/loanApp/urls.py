from django.urls import path
from . import views
from .views import completed_payments_chart, get_reference_numbers, sales_chart_data, test_send_loan_due_emails, upload_loans


urlpatterns = [
    path('index/', views.index, name='index'),
    path('index_staff/', views.index_staff, name='index_staff'),
    path('login/', views.login_view, name='login_view'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('test-send-loan-due-emails/', test_send_loan_due_emails, name='test_send_loan_due_emails'),

  


    # path('activeloans/', views.activeloans, name='activeloans'),
    # path('payments/', views.payments, name='payments'),
    # path('sales/', views.sales, name='sales'),

    # ActiveLoans URLs
    path('loans/', views.active_loans_list, name='active_loans_list'),
    path('loans/<int:pk>/', views.active_loans_detail, name='active_loans_detail'),
    path('loans/new/', views.active_loans_create, name='active_loans_create'),
    path('loans/<int:pk>/edit/', views.active_loans_update, name='active_loans_update'),
    path('loans/<int:pk>/delete/', views.active_loans_delete, name='active_loans_delete'),
    path('loans/<int:pk>/approve/', views.approve_loan, name='approve_loan'),
    
    # Payments URLs
    path('payments/', views.payments_list, name='payments_list'),
    path('payments/<int:pk>/', views.payments_detail, name='payments_detail'),
    path('payments/new/', views.payments_create, name='payments_create'),
    path('payments/<int:pk>/edit/', views.payments_update, name='payments_update'),
    path('payments/<int:pk>/delete/', views.payments_delete, name='payments_delete'),
    path('get_borrower_name/', views.get_borrower_name, name='get_borrower_name'),

    # Sales URLs
    path('sales/', views.sales_list, name='sales_list'),
    path('sales/<int:pk>/', views.sales_detail, name='sales_detail'),
    path('sales/new/', views.sales_create, name='sales_create'),
    path('sales/<int:pk>/edit/', views.sales_update, name='sales_update'),
    path('sales/<int:pk>/delete/', views.sales_delete, name='sales_delete'),
    path('get_collateral_info/', views.get_collateral_info, name='get_collateral_info'),
    path('sales_chart/', views.sales_chart, name='sales_chart'),
    path('sales/chart/', sales_chart_data, name='sales_chart_data'),
    path('get_reference_numbers/', get_reference_numbers, name='get_reference_numbers'),

    

    



    # Expenses URLs
    path('expenses/', views.expenses_list, name='expenses_list'),
    path('expenses/<int:pk>/', views.expenses_detail, name='expenses_detail'),
    path('expenses/new/', views.expenses_create, name='expenses_create'),
    path('expenses/<int:pk>/edit/', views.expenses_update, name='expenses_update'),
    path('expenses/<int:pk>/delete/', views.expenses_delete, name='expenses_delete'),

    # Trackers URLs
    path('trackers/', views.trackers_list, name='trackers_list'),
    path('trackers/<int:pk>/', views.trackers_detail, name='trackers_detail'),
    path('trackers/new/', views.trackers_create, name='trackers_create'),
    path('trackers/<int:pk>/edit/', views.trackers_update, name='tracker_update'),
    path('trackers/<int:pk>/delete/', views.trackers_delete, name='tracker_delete'),


    path('chart/loan-status/', views.loan_status_chart, name='loan_status_chart'),
    path('chart/payment-status/', views.payment_status_chart, name='payment_status_chart'),
    path('chart/sales/', views.sales_chart, name='sales_chart'),
    path('chart/expenses/', views.expenses_chart, name='expenses_chart'),
    path('chart/completed-payments/', completed_payments_chart, name='completed_payments_chart'),
    path('loans/status/chart/', views.active_loans_status_chart, name='active_loans_status_chart'),

    path('download-active-loans/', views.download_active_loans_excel, name='download_active_loans_excel'),
    
    # For the reports page itself
    path('reports/', views.reports_view, name='reports_view'),

    path('upload_loans/', upload_loans, name='upload_loans'),

    




]