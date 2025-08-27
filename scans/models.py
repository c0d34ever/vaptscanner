from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

# Define choices at module level to avoid circular dependencies
ENGINE_CHOICES = (
    ('zap', 'OWASP ZAP'),
    ('nmap', 'Nmap'),
    ('sqlmap', 'SQLMap'),
    ('wapiti', 'Wapiti'),
)

STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('IN_PROGRESS', 'In Progress'),
    ('COMPLETED', 'Completed'),
    ('FAILED', 'Failed'),
    ('CANCELLED', 'Cancelled'),
)

SEVERITY_CHOICES = (
    ('Critical', 'Critical'),
    ('High', 'High'),
    ('Medium', 'Medium'),
    ('Low', 'Low'),
    ('Info', 'Info'),
)

LEVEL_CHOICES = (
    ('DEBUG', 'Debug'),
    ('INFO', 'Info'),
    ('WARNING', 'Warning'),
    ('ERROR', 'Error'),
    ('CRITICAL', 'Critical'),
)


class ScanTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    engine = models.CharField(max_length=20, choices=ENGINE_CHOICES)
    options = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.name} ({self.engine})'


class ScheduledScan(models.Model):
    FREQUENCY_CHOICES = (
        ('once', 'Once'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )
    
    name = models.CharField(max_length=100)
    target_url = models.URLField()
    template = models.ForeignKey(ScanTemplate, on_delete=models.CASCADE, null=True, blank=True)
    engine = models.CharField(max_length=20, choices=ENGINE_CHOICES)
    options = models.JSONField(default=dict)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='once')
    next_run = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.name} - {self.frequency}'


class Scan(models.Model):
    target_url = models.URLField()
    engine = models.CharField(max_length=20, choices=ENGINE_CHOICES, default='zap')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    report_json = models.JSONField(null=True, blank=True)
    task_id = models.CharField(max_length=100, null=True, blank=True)
    options = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    command_output = models.TextField(null=True, blank=True)
    
    # New fields
    template = models.ForeignKey(ScanTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    scheduled_scan = models.ForeignKey(ScheduledScan, on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.IntegerField(default=5)  # 1=High, 5=Normal, 10=Low
    tags = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return f'Scan for {self.target_url} - {self.status}'

    @property
    def duration(self):
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        return None

    @property
    def findings_count(self):
        return self.findings.count()

    @property
    def critical_findings_count(self):
        return self.findings.filter(severity__in=['Critical', 'High']).count()


class Finding(models.Model):
    scan = models.ForeignKey(Scan, on_delete=models.CASCADE, related_name='findings')
    name = models.CharField(max_length=255)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    description = models.TextField()
    url = models.URLField()
    
    # New fields
    cve_id = models.CharField(max_length=50, blank=True)
    cvss_score = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    references = models.JSONField(default=list, blank=True)
    remediation = models.TextField(blank=True)
    false_positive = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    tags = models.JSONField(default=list, blank=True)

    def __str__(self) -> str:
        return f'{self.name} ({self.severity}) on {self.url}'


class ScanLog(models.Model):
    scan = models.ForeignKey(Scan, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='INFO')
    message = models.TextField()
    context = models.JSONField(null=True, blank=True)

    def __str__(self) -> str:
        return f'[{self.level}] {self.timestamp} - {self.message[:60]}'


class ScanComparison(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    scans = models.ManyToManyField(Scan, related_name='comparisons')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.name} ({self.scans.count()} scans)'


