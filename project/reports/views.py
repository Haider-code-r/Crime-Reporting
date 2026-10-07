from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from functools import wraps
from .models import CrimeReport, PoliceOfficer
from .forms import (
    RegisterForm, LoginForm, CrimeReportForm, StatusUpdateForm,
    PoliceLoginForm, PoliceRegisterForm,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helper: Police-only decorator
# ─────────────────────────────────────────────────────────────────────────────

def police_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login as a police officer.')
            return redirect('police_login')
        if not hasattr(request.user, 'police_profile') and not request.user.is_superuser:
            messages.error(request, 'Access denied. Police officers only.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def superuser_required(view_func):
    """Only logged-in superusers (system administrators) may pass."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url='/login/')
        if not request.user.is_superuser:
            messages.error(request, 'Only the system administrator can register police officers.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─────────────────────────────────────────────────────────────────────────────
# Citizen Auth
# ─────────────────────────────────────────────────────────────────────────────

def home_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'police_profile'):
            return redirect('police_dashboard')
        return redirect('dashboard')
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Welcome, {user.first_name}! Your account has been created.')
        return redirect('dashboard')
    return render(request, 'reports/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if hasattr(user, 'police_profile'):
            messages.error(request, 'Police officers must use the Police Login portal.')
            return redirect('police_login')
        login(request, user)
        messages.success(request, f'Welcome back, {user.first_name or user.username}!')
        return redirect(request.GET.get('next', 'dashboard'))
    return render(request, 'reports/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out safely.')
    return redirect('login')


# ─────────────────────────────────────────────────────────────────────────────
# Citizen: dashboard, file a report, track a report
# (citizen sirf report file kar sakta hai aur track kar sakta hai)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def dashboard_view(request):
    if hasattr(request.user, 'police_profile'):
        return redirect('police_dashboard')
    my_reports = CrimeReport.objects.filter(reporter=request.user)
    return render(request, 'reports/dashboard.html', {
        'total': my_reports.count(),
        'reports': my_reports,
    })


@login_required
def report_create_view(request):
    if hasattr(request.user, 'police_profile'):
        return redirect('police_dashboard')
    form = CrimeReportForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        report = form.save(commit=False)
        if not form.cleaned_data.get('is_anonymous'):
            report.reporter = request.user
        report.save()
        # Tracking number wali simple page par bhejo (anonymous reports ke liye bhi chalta hai)
        return redirect('report_submitted', report_id=report.report_id)
    return render(request, 'reports/report_form.html', {'form': form, 'title': 'File New Report'})


@login_required
def report_submitted_view(request, report_id):
    """Report file hone ke baad citizen ko uska tracking number dikhata hai."""
    report = get_object_or_404(CrimeReport, report_id=report_id)
    return render(request, 'reports/report_submitted.html', {'report': report})


def track_view(request):
    report = None
    error = None
    uid = (request.POST.get('report_id') or request.GET.get('report_id') or '').strip()
    if uid:
        try:
            report = CrimeReport.objects.get(report_id=uid)
        except (CrimeReport.DoesNotExist, ValidationError, ValueError):
            error = 'No report found with that tracking number.'
    return render(request, 'reports/track.html', {'report': report, 'error': error})


# ─────────────────────────────────────────────────────────────────────────────
# Police Auth  (accounts created by Admin only via /admin/)
# ─────────────────────────────────────────────────────────────────────────────


def police_login_view(request):
    if request.user.is_authenticated and hasattr(request.user, 'police_profile'):
        return redirect('police_dashboard')
    form = PoliceLoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if not hasattr(user, 'police_profile'):
            messages.error(request, 'This account is not registered as a police officer.')
            return render(request, 'reports/police_login.html', {'form': form})
        login(request, user)
        messages.success(request, f'Welcome, {user.police_profile.get_rank_display()} {user.last_name}!')
        return redirect('police_dashboard')
    return render(request, 'reports/police_login.html', {'form': form})


@superuser_required
def police_register_view(request):
    """Admin-only page: creates a police User + PoliceOfficer profile together."""
    form = PoliceRegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(
            request,
            f"Officer {user.get_full_name()} registered "
            f"(badge {form.cleaned_data['badge_number']}). They can now log in at the Police Portal."
        )
        return redirect('police_register')
    officers = PoliceOfficer.objects.select_related('user').order_by('-created_at')[:10]
    return render(request, 'reports/police_register.html', {'form': form, 'officers': officers})


def police_logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Logged out of Police Portal.')
    return redirect('police_login')


# ─────────────────────────────────────────────────────────────────────────────
# Police Portal Views
# ─────────────────────────────────────────────────────────────────────────────

@police_required
def police_dashboard_view(request):
    officer = getattr(request.user, 'police_profile', None)
    all_reports = CrimeReport.objects.all()
    stats = {
        'total':         all_reports.count(),
        'pending':       all_reports.filter(status='pending').count(),
        'investigating': all_reports.filter(status='investigating').count(),
        'resolved':      all_reports.filter(status='resolved').count(),
        'critical':      all_reports.filter(priority='critical').count(),
    }
    return render(request, 'reports/police_dashboard.html', {
        'officer': officer, 'stats': stats, 'recent': all_reports[:6],
    })


@police_required
def police_report_list_view(request):
    qs = CrimeReport.objects.all()
    q               = request.GET.get('q', '')
    status_filter   = request.GET.get('status', '')
    type_filter     = request.GET.get('crime_type', '')
    priority_filter = request.GET.get('priority', '')
    if q:
        qs = qs.filter(Q(title__icontains=q)|Q(description__icontains=q)|Q(location__icontains=q)|Q(city__icontains=q)|Q(suspect_name__icontains=q))
    if status_filter:
        qs = qs.filter(status=status_filter)
    if type_filter:
        qs = qs.filter(crime_type=type_filter)
    if priority_filter:
        qs = qs.filter(priority=priority_filter)
    return render(request, 'reports/police_report_list.html', {
        'reports': qs, 'q': q,
        'status_filter': status_filter, 'type_filter': type_filter, 'priority_filter': priority_filter,
        'status_choices': CrimeReport.STATUS_CHOICES,
        'type_choices': CrimeReport.CRIME_TYPES,
        'priority_choices': CrimeReport.PRIORITY_CHOICES,
        'total_count': qs.count(),
    })


@police_required
def police_report_detail_view(request, pk):
    report = get_object_or_404(CrimeReport, pk=pk)
    status_form = StatusUpdateForm(request.POST or None, instance=report)
    if request.method == 'POST' and status_form.is_valid():
        status_form.save()
        messages.success(request, f'Report #{report.short_id()} updated.')
        return redirect('police_report_detail', pk=pk)
    return render(request, 'reports/police_report_detail.html', {
        'report': report, 'status_form': status_form, 'officer': getattr(request.user, 'police_profile', None),
    })


def admin_blocked_view(request):
    return render(request, 'reports/admin_blocked.html', status=403)
