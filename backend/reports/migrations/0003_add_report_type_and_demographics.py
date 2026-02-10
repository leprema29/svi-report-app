# Generated migration for report type and demographics fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_add_pptx_and_new_kpis'),
    ]

    operations = [
        migrations.AddField(
            model_name='surveillancereport',
            name='report_type',
            field=models.CharField(
                choices=[
                    ('mention_dashboard', 'Mention.com Dashboard'),
                    ('brand24_analysis', 'Brand24 Analysis'),
                    ('brand24_demographics', 'Brand24 Demographics'),
                    ('unknown', 'Unknown'),
                ],
                default='unknown',
                max_length=50
            ),
        ),
        migrations.AddField(
            model_name='surveillancereport',
            name='report_type_display',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='surveillancereport',
            name='demographics_data',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='surveillancereport',
            name='available_kpis',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='surveillancereport',
            name='unavailable_kpis',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
