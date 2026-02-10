# Generated migration for reach_breakdown_data field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_add_report_type_and_demographics'),
    ]

    operations = [
        migrations.AddField(
            model_name='surveillancereport',
            name='reach_breakdown_data',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
