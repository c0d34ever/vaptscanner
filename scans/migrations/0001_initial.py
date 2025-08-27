from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Scan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_url', models.URLField()),
                ('engine', models.CharField(choices=[('zap', 'OWASP ZAP'), ('nmap', 'Nmap'), ('sqlmap', 'SQLMap'), ('wapiti', 'Wapiti')], default='zap', max_length=20)),
                ('status', models.CharField(default='PENDING', max_length=20)),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('report_json', models.JSONField(blank=True, null=True)),
                ('task_id', models.CharField(blank=True, max_length=100, null=True)),
                ('options', models.JSONField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('command_output', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Finding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('severity', models.CharField(max_length=20)),
                ('description', models.TextField()),
                ('url', models.URLField()),
                ('scan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='findings', to='scans.scan')),
            ],
        ),
    ]


