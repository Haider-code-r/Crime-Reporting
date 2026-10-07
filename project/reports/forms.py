from django import forms
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import CrimeReport, PoliceOfficer


# ── Widget helper ────────────────────────────────────────────────────────────
def inp(placeholder='', extra=''):
    return {'class': f'form-input {extra}'.strip(), 'placeholder': placeholder}

def sel():
    return {'class': 'form-input form-select'}

def ta(placeholder='', rows=4):
    return {'class': 'form-input form-textarea', 'placeholder': placeholder, 'rows': rows}


# ── Auth Forms ────────────────────────────────────────────────────────────────
class RegisterForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs=inp('First Name')))
    last_name  = forms.CharField(widget=forms.TextInput(attrs=inp('Last Name')))
    email      = forms.EmailField(required=True, widget=forms.EmailInput(attrs=inp('Email Address')))
    username   = forms.CharField(widget=forms.TextInput(attrs=inp('Username')))
    password1  = forms.CharField(label='Password',
                                 widget=forms.PasswordInput(attrs=inp('Password')))
    password2  = forms.CharField(label='Confirm Password',
                                 widget=forms.PasswordInput(attrs=inp('Confirm Password')))

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={**inp('Username'), 'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs=inp('Password')))


# ── Crime Report Form ─────────────────────────────────────────────────────────
class CrimeReportForm(forms.ModelForm):

    class Meta:
        model  = CrimeReport
        fields = [
            'is_anonymous',
            'crime_type', 'title', 'description',
            'incident_date', 'incident_time',
            'location', 'city', 'state', 'pincode',
            'suspect_name', 'suspect_desc',
            'evidence_image',
        ]
        widgets = {
            'is_anonymous':   forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'crime_type':     forms.Select(attrs=sel()),
            'title':          forms.TextInput(attrs=inp('Brief title of the incident')),
            'description':    forms.Textarea(attrs=ta('Describe what happened in detail...', 5)),
            'incident_date':  forms.DateInput(attrs={**inp(''), 'type': 'date', 'class': 'form-input'}),
            'incident_time':  forms.TimeInput(attrs={**inp(''), 'type': 'time', 'class': 'form-input'}),
            'location':       forms.TextInput(attrs=inp('Street / Landmark / Area')),
            'city':           forms.TextInput(attrs=inp('City')),
            'state':          forms.TextInput(attrs=inp('State')),
            'pincode':        forms.TextInput(attrs=inp('Pincode')),
            'suspect_name':   forms.TextInput(attrs=inp('Name (if known)')),
            'suspect_desc':   forms.Textarea(attrs=ta('Physical description, vehicle, etc.', 3)),
            'evidence_image': forms.FileInput(attrs={'class': 'form-file'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['incident_time'].required = False
        self.fields['pincode'].required       = False
        self.fields['suspect_name'].required  = False
        self.fields['suspect_desc'].required  = False
        self.fields['evidence_image'].required = False


# ── Admin Status Update Form ──────────────────────────────────────────────────
class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model  = CrimeReport
        fields = ['status', 'priority', 'admin_notes']
        widgets = {
            'status':      forms.Select(attrs=sel()),
            'priority':    forms.Select(attrs=sel()),
            'admin_notes': forms.Textarea(attrs=ta('Add investigation notes...', 4)),
        }


# ── Police Login Form ─────────────────────────────────────────────────────────
# Police accounts are created by Admin only via /admin/ — no self-registration
class PoliceLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={**inp('Username'), 'autofocus': True})
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs=inp('Password')))


# ── Police Registration Form (used only on the superuser-only page) ──────────
class PoliceRegisterForm(UserCreationForm):
    """Creates a User AND its PoliceOfficer profile in one step."""
    first_name   = forms.CharField(max_length=150)
    last_name    = forms.CharField(max_length=150)
    email        = forms.EmailField()
    badge_number = forms.CharField(max_length=20, label='Badge / ID Number')
    rank         = forms.ChoiceField(choices=PoliceOfficer.RANK_CHOICES)
    station      = forms.CharField(max_length=200)
    district     = forms.CharField(max_length=100)
    phone        = forms.CharField(max_length=15, required=False)
    joined_date  = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'username': 'e.g. badge number',
            'badge_number': 'e.g. PC1001',
        }
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input form-select' if name == 'rank' else 'form-input'
            if name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[name]

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_badge_number(self):
        badge = self.cleaned_data['badge_number'].strip()
        if PoliceOfficer.objects.filter(badge_number__iexact=badge).exists():
            raise forms.ValidationError('This badge number is already registered.')
        return badge

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = False
        user.is_superuser = False
        if commit:
            with transaction.atomic():
                user.save()
                PoliceOfficer.objects.create(
                    user         = user,
                    badge_number = self.cleaned_data['badge_number'],
                    rank         = self.cleaned_data['rank'],
                    station      = self.cleaned_data['station'],
                    district     = self.cleaned_data['district'],
                    phone        = self.cleaned_data.get('phone', ''),
                    joined_date  = self.cleaned_data.get('joined_date'),
                )
        return user
