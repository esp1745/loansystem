from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from django import forms
from .models import ActiveLoans, Document
from .models import ActiveLoans, Payments, Sales, Expenses, Trackers

from django.contrib.auth.models import Group


from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class LoginForm(forms.Form):
    username = forms.CharField(
        widget= forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    email = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'is_admin', 'is_employee')



class ActiveLoansForm(forms.ModelForm):
    class Meta:
        model = ActiveLoans
        fields = [
            'borrower_name',
            'nrc_number',
            'phone_number',
            'collateral_name',
            'address',
            'loan_date',
            'loan_due_date',
            'principle_amount',
            'interest_amount',
            'total_loan_amount',
            'status',
        ]

    loan_date = forms.DateField(
        input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'],
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    loan_due_date = forms.DateField(
        input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'],
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ActiveLoansForm, self).__init__(*args, **kwargs)
        if user and not user.is_admin:
            self.fields['status'].choices = [('pending_approval', 'Pending Approval')]
            self.fields['status'].initial = 'pending_approval'
            self.fields['status'].widget = forms.HiddenInput()

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file']

DocumentFormSet = forms.inlineformset_factory(ActiveLoans, Document, form=DocumentForm, extra=1, can_delete=True)


class PaymentsForm(forms.ModelForm):
    reference_number = forms.ModelChoiceField(
        queryset=ActiveLoans.objects.all(),
        empty_label="Select a Loan",
        to_field_name="reference_number",  # Use this if reference_number is unique
        widget=forms.Select(attrs={'onchange': 'updateBorrowerName()'})
    )

    class Meta:
        model = Payments
        fields = ['borrower_name', 'total_loan_amount', 'reference_number', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].required = False  # Adjust as needed

from django import forms
from .models import Sales, ActiveLoans

from django import forms
from .models import Sales, ActiveLoans

class SalesForm(forms.ModelForm):
    reference_number = forms.ModelChoiceField(queryset=ActiveLoans.objects.all(), to_field_name="reference_number")

    class Meta:
        model = Sales
        fields = ['reference_number', 'collateral_name', 'collateral_amount', 'actual_amount_sold', 'profit_or_loss']
        widgets = {
            'collateral_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'collateral_amount': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'profit_or_loss': forms.NumberInput(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['collateral_name'].required = False
        self.fields['collateral_amount'].required = False
        self.fields['profit_or_loss'].required = False

    def clean(self):
        cleaned_data = super().clean()
        reference_number_obj = cleaned_data.get("reference_number")
        actual_amount_sold = cleaned_data.get("actual_amount_sold")

        if reference_number_obj:
            reference_number = reference_number_obj.reference_number
            print("Reference Number from Form:", reference_number)

            try:
                loan = ActiveLoans.objects.get(reference_number=reference_number)
                print("Loan Found:", loan)
                cleaned_data['collateral_name'] = loan.collateral_name
                cleaned_data['collateral_amount'] = loan.total_loan_amount
            except ActiveLoans.DoesNotExist:
                print("Loan Not Found for Reference Number:", reference_number)
                self.add_error('reference_number', 'The selected reference number does not exist.')

        if actual_amount_sold is not None:
            collateral_amount = cleaned_data.get('collateral_amount')
            cleaned_data['profit_or_loss'] = actual_amount_sold - collateral_amount

        return cleaned_data


class ExpensesForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = '__all__'

class TrackerForm(forms.ModelForm):
    class Meta:
        model = Trackers
        fields = ['tracking_number', 'phone_number', 'client_name','status']




class UploadExcelForm(forms.Form):
    file = forms.FileField()
