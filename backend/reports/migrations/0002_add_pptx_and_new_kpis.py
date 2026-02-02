# Generated manually for PPTX support and new KPI fields

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        # Add original_file field for both PDF and PPTX
        migrations.AddField(
            model_name='surveillancereport',
            name='original_file',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to='reports/uploads/%Y/%m/',
                validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'pptx'])]
            ),
        ),
        # Add file_type field
        migrations.AddField(
            model_name='surveillancereport',
            name='file_type',
            field=models.CharField(
                choices=[('pdf', 'PDF'), ('pptx', 'PPTX')],
                default='pdf',
                max_length=10
            ),
        ),
        # Add presence_passive_data field
        migrations.AddField(
            model_name='surveillancereport',
            name='presence_passive_data',
            field=models.JSONField(blank=True, default=dict),
        ),
        # Add presence_active_data field
        migrations.AddField(
            model_name='surveillancereport',
            name='presence_active_data',
            field=models.JSONField(blank=True, default=dict),
        ),
        # Make original_pdf optional (nullable)
        migrations.AlterField(
            model_name='surveillancereport',
            name='original_pdf',
            field=models.FileField(blank=True, null=True, upload_to='reports/pdf/%Y/%m/'),
        ),
    ]
