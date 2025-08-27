from django.db import models


class Scan(models.Model):
    ENGINE_CHOICES = (
        ('zap', 'OWASP ZAP'),
        ('nmap', 'Nmap'),
        ('sqlmap', 'SQLMap'),
        ('wapiti', 'Wapiti'),
    )

    target_url = models.URLField()
    engine = models.CharField(max_length=20, choices=ENGINE_CHOICES, default='zap')
    status = models.CharField(max_length=20, default='PENDING')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    report_json = models.JSONField(null=True, blank=True)
    task_id = models.CharField(max_length=100, null=True, blank=True)
    options = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    command_output = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f'Scan for {self.target_url} - {self.status}'


class Finding(models.Model):
    scan = models.ForeignKey(Scan, on_delete=models.CASCADE, related_name='findings')
    name = models.CharField(max_length=255)
    severity = models.CharField(max_length=20)
    description = models.TextField()
    url = models.URLField()

    def __str__(self) -> str:
        return f'{self.name} ({self.severity}) on {self.url}'


