from django.db import models
from django.contrib.auth.models import User
import uuid


class PoliceOfficer(models.Model):
    """Extended profile for police officer accounts."""

    RANK_CHOICES = [
        ('constable',    'Constable'),
        ('hc',           'Head Constable'),
        ('asi',          'ASI'),
        ('si',           'Sub-Inspector'),
        ('inspector',    'Inspector'),
        ('ci',           'Circle Inspector'),
        ('dsp',          'DSP'),
        ('sp',           'Superintendent of Police'),
    ]

    user            = models.OneToOneField(User, on_delete=models.CASCADE, related_name='police_profile')
    badge_number    = models.CharField(max_length=20, unique=True)
    rank            = models.CharField(max_length=20, choices=RANK_CHOICES, default='constable')
    station         = models.CharField(max_length=200)
    district        = models.CharField(max_length=100)
    phone           = models.CharField(max_length=15, blank=True)
    is_active_duty  = models.BooleanField(default=True)
    joined_date     = models.DateField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Police Officer'
        verbose_name_plural = 'Police Officers'

    def __str__(self):
        return f"{self.get_rank_display()} {self.user.get_full_name()} [{self.badge_number}]"


class CrimeReport(models.Model):

    # ── Crime Type Choices ──────────────────────────────────────────────
    CRIME_TYPES = [
        ('theft',           'Theft / Burglary'),
        ('assault',         'Assault / Physical violence'),
        ('cybercrime',      'Cybercrime / Online fraud'),
        ('harassment',      'Harassment / Stalking'),
        ('vandalism',       'Vandalism / Property damage'),
        ('drug',            'Drug related'),
        ('fraud',           'Financial fraud / Scam'),
        ('missing_person',  'Missing person'),
        ('accident',        'Road accident'),
        ('other',           'Other'),
    ]

    # ── Status Choices ───────────────────────────────────────────────────
    STATUS_CHOICES = [
        ('pending',      'Pending'),
        ('investigating','Under Investigation'),
        ('resolved',     'Resolved'),
        ('closed',       'Closed'),
    ]

    # ── Priority Choices ─────────────────────────────────────────────────
    PRIORITY_CHOICES = [
        ('low',      'Low'),
        ('medium',   'Medium'),
        ('high',     'High'),
        ('critical', 'Critical'),
    ]

    # ── Core Fields ──────────────────────────────────────────────────────
    report_id       = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    reporter        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='reports')
    is_anonymous    = models.BooleanField(default=False)

    # ── Incident Details ─────────────────────────────────────────────────
    crime_type      = models.CharField(max_length=30, choices=CRIME_TYPES)
    title           = models.CharField(max_length=200)
    description     = models.TextField()
    incident_date   = models.DateField()
    incident_time   = models.TimeField(null=True, blank=True)

    # ── Location ─────────────────────────────────────────────────────────
    location        = models.CharField(max_length=300)
    city            = models.CharField(max_length=100)
    state           = models.CharField(max_length=100, default='Telangana')
    pincode         = models.CharField(max_length=10, blank=True)

    # ── Suspect Info (optional) ───────────────────────────────────────────
    suspect_name    = models.CharField(max_length=200, blank=True)
    suspect_desc    = models.TextField(blank=True, verbose_name='Suspect Description')

    # ── Evidence ─────────────────────────────────────────────────────────
    evidence_image  = models.ImageField(upload_to='evidence/', null=True, blank=True)

    # ── Status & Admin ───────────────────────────────────────────────────
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority        = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    admin_notes     = models.TextField(blank=True)

    # ── Timestamps ───────────────────────────────────────────────────────
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Crime Report'
        verbose_name_plural = 'Crime Reports'

    def __str__(self):
        return f"[{self.get_status_display()}] {self.title} — {self.get_crime_type_display()}"

    def short_id(self):
        return str(self.report_id).upper()[:8]

    def status_step(self):
        """Position of the current status in the workflow (1-4), used by the tracking page."""
        order = [key for key, _ in self.STATUS_CHOICES]
        return order.index(self.status) + 1 if self.status in order else 1

    def status_color(self):
        return {
            'pending':       '#f59e0b',
            'investigating': '#3b82f6',
            'resolved':      '#10b981',
            'closed':        '#6b7280',
        }.get(self.status, '#6b7280')

    def priority_color(self):
        return {
            'low':      '#10b981',
            'medium':   '#f59e0b',
            'high':     '#ef4444',
            'critical': '#dc2626',
        }.get(self.priority, '#6b7280')
