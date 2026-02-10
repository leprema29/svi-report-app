"""
Celery Tasks for Report Processing
"""
from celery import shared_task
from django.core.files import File
from datetime import datetime
import os
import logging

from .models import SurveillanceReport
from .services.pdf_extractor import extract_kpis_from_pdf
from .services.pptx_extractor import extract_kpis_from_pptx
from .services.word_generator import generate_word_report

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_surveillance_report(self, report_id: int):
    """
    Process uploaded PDF/PPTX report asynchronously
    - Extract KPIs from PDF or PPTX
    - Generate Word document
    - Update database
    """
    try:
        # Get report instance
        report = SurveillanceReport.objects.get(id=report_id)
        report.status = 'processing'
        report.save()

        # Determine file type and get file path
        if report.original_file:
            file_path = report.original_file.path
            file_type = report.file_type
        elif report.original_pdf:
            file_path = report.original_pdf.path
            file_type = 'pdf'
        else:
            raise ValueError("No file found for this report")

        # Extract KPIs based on file type
        logger.info(f"Extracting KPIs from {file_type.upper()} for report {report_id}")

        if file_type == 'pptx':
            extracted_data = extract_kpis_from_pptx(file_path)
        else:
            extracted_data = extract_kpis_from_pdf(file_path)

        # Update report with extracted data (legacy fields)
        report.total_mentions = extracted_data.get('volume', {}).get('mentions', 0)
        report.mentions_change_percent = extracted_data.get('volume', {}).get('change_percent', 0)
        report.total_reach = extracted_data.get('reach', {}).get('reach', 0)
        report.reach_change_percent = extracted_data.get('reach', {}).get('change_percent', 0)

        # Update new KPI fields
        report.presence_passive_data = extracted_data.get('presence_passive', {})
        report.presence_active_data = extracted_data.get('presence_active', {})

        # Parse dates
        period = extracted_data.get('period', {})
        if period.get('start'):
            try:
                # Try multiple date formats
                date_formats = ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d']
                for fmt in date_formats:
                    try:
                        report.period_start = datetime.strptime(period['start'], fmt).date()
                        break
                    except ValueError:
                        continue
            except:
                pass
        if period.get('end'):
            try:
                date_formats = ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d']
                for fmt in date_formats:
                    try:
                        report.period_end = datetime.strptime(period['end'], fmt).date()
                        break
                    except ValueError:
                        continue
            except:
                pass

        # Store report type info
        report.report_type = extracted_data.get('report_type', 'unknown')
        report.report_type_display = extracted_data.get('report_type_display', '')
        report.available_kpis = extracted_data.get('available_kpis', [])
        report.unavailable_kpis = extracted_data.get('unavailable_kpis', [])

        # Store JSON data
        report.sentiment_data = extracted_data.get('sentiment', {})
        report.emotion_data = extracted_data.get('emotion', {})
        report.sources_data = extracted_data.get('sources', {})
        report.languages_data = extracted_data.get('languages', {})
        report.topics_data = extracted_data.get('topics', [])
        report.hashtags_data = extracted_data.get('hashtags', [])
        report.influencers_data = extracted_data.get('influencers', [])
        report.reach_breakdown_data = extracted_data.get('reach_breakdown', [])

        # Store demographics data (for Brand24 Demographics reports)
        report.demographics_data = extracted_data.get('demographics', {})

        report.save()

        # Generate Word document
        logger.info(f"Generating Word document for report {report_id}")
        output_dir = os.path.dirname(file_path)
        output_filename = f"report_{report_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        output_path = os.path.join(output_dir, output_filename)

        # Add title and source filename to extracted data for Word generation
        extracted_data['title'] = report.title
        extracted_data['source_filename'] = os.path.basename(file_path)

        generate_word_report(extracted_data, output_path)

        # Save generated document to model
        with open(output_path, 'rb') as docx_file:
            report.generated_docx.save(output_filename, File(docx_file), save=True)

        # Clean up temporary file
        if os.path.exists(output_path):
            os.remove(output_path)

        # Mark as completed
        report.status = 'completed'
        report.save()

        logger.info(f"Report {report_id} processed successfully")
        return {'status': 'success', 'report_id': report_id}

    except SurveillanceReport.DoesNotExist:
        logger.error(f"Report {report_id} not found")
        return {'status': 'error', 'message': 'Report not found'}

    except Exception as e:
        logger.error(f"Error processing report {report_id}: {str(e)}")

        # Update report status
        try:
            report = SurveillanceReport.objects.get(id=report_id)
            report.status = 'failed'
            report.error_message = str(e)
            report.save()
        except:
            pass

        # Retry task
        raise self.retry(exc=e, countdown=60)
