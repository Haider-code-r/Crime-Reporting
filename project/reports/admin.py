from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CrimeReport, PoliceOfficer


# ── Inline: show PoliceOfficer fields inside User admin ──────────────────────
class PoliceOfficerInline(admin.StackedInline):
    model       = PoliceOfficer
    can_delete  = False
    verbose_name = 'Police Officer Profile'
    fields      = ['badge_number', 'rank', 'station', 'district', 'phone', 'joined_date', 'is_active_duty']
    extra       = 0


# ── Custom User Creation Form used inside Django Admin ───────────────────────
class PoliceUserCreationForm(UserCreationForm):
    """Used by admin when adding a new police officer."""
    first_name   = forms.CharField(required=True)
    last_name    = forms.CharField(required=True)
    email        = forms.EmailField(required=True)
    badge_number = forms.CharField(max_length=20, required=True, label='Badge / ID Number')
    rank         = forms.ChoiceField(choices=PoliceOfficer.RANK_CHOICES)
    station      = forms.CharField(max_length=200)
    district     = forms.CharField(max_length=100)
    phone        = forms.CharField(max_length=15, required=False)
    joined_date  = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        user.email      = self.cleaned_data['email']
        user.is_staff   = False
        user.is_superuser = False
        if commit:
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


# ── Custom Admin for Police User creation ────────────────────────────────────
class PoliceUserAdmin(admin.ModelAdmin):
    """Dedicated admin view to add/manage police officers."""
    form         = PoliceUserCreationForm
    add_form     = PoliceUserCreationForm
    list_display = ['badge_number', 'full_name', 'rank', 'station', 'district', 'is_active_duty', 'created_at']
    list_filter  = ['rank', 'district', 'is_active_duty']
    search_fields = ['badge_number', 'user__username', 'user__first_name', 'user__last_name', 'station']
    readonly_fields = ['created_at']
    ordering     = ['rank', 'user__last_name']

    fieldsets = (
        ('Account Credentials', {
            'fields': ('user',),
            'description': 'Linked Django user account.',
        }),
        ('Officer Details', {
            'fields': ('badge_number', 'rank', 'station', 'district', 'phone', 'joined_date', 'is_active_duty'),
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    full_name.short_description = 'Name'


# ── Crime Report Admin ────────────────────────────────────────────────────────
@admin.register(CrimeReport)
class CrimeReportAdmin(admin.ModelAdmin):
    list_display   = ['short_id', 'title', 'crime_type', 'status', 'priority', 'city', 'created_at']
    list_filter    = ['status', 'priority', 'crime_type', 'created_at']
    search_fields  = ['title', 'description', 'location', 'city']
    readonly_fields = ['report_id', 'created_at', 'updated_at']
    list_editable  = ['status', 'priority']
    ordering       = ['-created_at']

    fieldsets = (
        ('Report Identity', {
            'fields': ('report_id', 'reporter', 'is_anonymous')
        }),
        ('Incident Details', {
            'fields': ('crime_type', 'title', 'description', 'incident_date', 'incident_time')
        }),
        ('Location', {
            'fields': ('location', 'city', 'state', 'pincode')
        }),
        ('Suspect Info', {
            'fields': ('suspect_name', 'suspect_desc'),
            'classes': ('collapse',),
        }),
        ('Evidence', {
            'fields': ('evidence_image',),
        }),
        ('Status & Admin', {
            'fields': ('status', 'priority', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


# ── Register PoliceOfficer standalone ────────────────────────────────────────
@admin.register(PoliceOfficer)
class PoliceOfficerAdmin(admin.ModelAdmin):
    list_display   = ['badge_number', 'get_full_name', 'rank', 'station', 'district', 'is_active_duty']
    list_filter    = ['rank', 'district', 'is_active_duty']
    search_fields  = ['badge_number', 'user__username', 'user__first_name', 'station']
    readonly_fields = ['created_at']
    list_editable  = ['is_active_duty']

    fieldsets = (
        ('Officer Account', {
            'fields': ('user', 'badge_number', 'rank'),
            'description': '⚠ To create a NEW police officer, use the "Add Police Officer" button. '
                           'This assigns a Django user AND creates the profile together.',
        }),
        ('Station Details', {
            'fields': ('station', 'district', 'phone', 'joined_date'),
        }),
        ('Status', {
            'fields': ('is_active_duty', 'created_at'),
        }),
    )

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Full Name'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            # Adding new officer — show helpful note
            form.base_fields['user'].help_text = (
                'First create a User account, then link it here. '
                'Or use the PoliceOfficer admin add form which creates both together.'
            )
        return form
