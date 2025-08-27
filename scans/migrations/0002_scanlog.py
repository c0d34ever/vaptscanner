from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('scans', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScanLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('level', models.CharField(default='INFO', max_length=10)),
                ('message', models.TextField()),
                ('context', models.JSONField(blank=True, null=True)),
                ('scan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='scans.scan')),
            ],
        ),
    ]


