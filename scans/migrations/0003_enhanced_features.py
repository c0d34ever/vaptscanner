from django.db import migrations, models
import django.db.models.deletion
import django.contrib.auth.models


class Migration(migrations.Migration):
    dependencies = [
        ('scans', '0002_scanlog'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScanTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('engine', models.CharField(choices=[('zap', 'OWASP ZAP'), ('nmap', 'Nmap'), ('sqlmap', 'SQLMap'), ('wapiti', 'Wapiti')], max_length=20)),
                ('options', models.JSONField(default=dict)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='ScheduledScan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('target_url', models.URLField()),
                ('engine', models.CharField(choices=[('zap', 'OWASP ZAP'), ('nmap', 'Nmap'), ('sqlmap', 'SQLMap'), ('wapiti', 'Wapiti')], max_length=20)),
                ('options', models.JSONField(default=dict)),
                ('frequency', models.CharField(choices=[('once', 'Once'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], default='once', max_length=20)),
                ('next_run', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
                ('template', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='scans.scantemplate')),
            ],
        ),
        migrations.CreateModel(
            name='ScanComparison',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
                ('scans', models.ManyToManyField(related_name='comparisons', to='scans.scan')),
            ],
        ),
        migrations.AddField(
            model_name='scan',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user'),
        ),
        migrations.AddField(
            model_name='scan',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='scan',
            name='priority',
            field=models.IntegerField(default=5),
        ),
        migrations.AddField(
            model_name='scan',
            name='scheduled_scan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='scans.scheduledscan'),
        ),
        migrations.AddField(
            model_name='scan',
            name='tags',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='scan',
            name='template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='scans.scantemplate'),
        ),
        migrations.AddField(
            model_name='finding',
            name='cve_id',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='finding',
            name='cvss_score',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True),
        ),
        migrations.AddField(
            model_name='finding',
            name='false_positive',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='finding',
            name='remediation',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='finding',
            name='references',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='finding',
            name='tags',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='finding',
            name='verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='finding',
            name='severity',
            field=models.CharField(choices=[('Critical', 'Critical'), ('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low'), ('Info', 'Info')], max_length=20),
        ),
        migrations.AlterField(
            model_name='scan',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=20),
        ),
        migrations.AlterField(
            model_name='scanlog',
            name='level',
            field=models.CharField(choices=[('DEBUG', 'Debug'), ('INFO', 'Info'), ('WARNING', 'Warning'), ('ERROR', 'Error'), ('CRITICAL', 'Critical')], default='INFO', max_length=10),
        ),
    ]
