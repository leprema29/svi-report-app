"""
Celery Tasks for Report Processing
"""
from celery import shared_task
from django.core.files import File
from datetime import datetime
import os
import logging

from .models import SurveillanceReport, ReportGroup
from .services.pdf_extractor import extract_kpis_from_pdf
from .services.pptx_extractor import extract_kpis_from_pptx
from .services.word_generator import generate_word_report
from .services.data_merger import merge_multiple_reports

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


@shared_task(bind=True, max_retries=3)
def process_report_group(self, group_id: int):
    """
    Process a report group with multiple source files
    - Extract KPIs from each source file (PDF or PPTX)
    - Merge data from all sources
    - Generate comprehensive Word document
    - Update database
    """
    try:
        # Get report group instance
        report_group = ReportGroup.objects.get(id=group_id)
        report_group.status = 'processing'
        report_group.save()

        # Get all source reports in this group
        source_reports = report_group.source_reports.all()

        if not source_reports.exists():
            raise ValueError("No source reports found in this group")

        logger.info(f"Processing report group {group_id} with {source_reports.count()} source files")

        # Process each source report and collect extracted data
        reports_data = []
        report_types = []

        for report in source_reports:
            # Mark individual report as processing
            report.status = 'processing'
            report.save()

            try:
                # Determine file type and get file path
                if report.original_file:
                    file_path = report.original_file.path
                    file_type = report.file_type
                elif report.original_pdf:
                    file_path = report.original_pdf.path
                    file_type = 'pdf'
                else:
                    logger.warning(f"No file found for report {report.id}, skipping")
                    report.status = 'failed'
                    report.error_message = "No file found"
                    report.save()
                    continue

                # Extract KPIs based on file type
                logger.info(f"Extracting KPIs from {file_type.upper()} for report {report.id}")

                if file_type == 'pptx':
                    extracted_data = extract_kpis_from_pptx(file_path)
                else:
                    extracted_data = extract_kpis_from_pdf(file_path)

                # Update individual report with extracted data
                report.total_mentions = extracted_data.get('volume', {}).get('mentions', 0)
                report.mentions_change_percent = extracted_data.get('volume', {}).get('change_percent', 0)
                report.total_reach = extracted_data.get('reach', {}).get('reach', 0)
                report.reach_change_percent = extracted_data.get('reach', {}).get('change_percent', 0)
                report.presence_passive_data = extracted_data.get('presence_passive', {})
                report.presence_active_data = extracted_data.get('presence_active', {})
                report.report_type = extracted_data.get('report_type', 'unknown')
                report.report_type_display = extracted_data.get('report_type_display', '')
                report.available_kpis = extracted_data.get('available_kpis', [])
                report.unavailable_kpis = extracted_data.get('unavailable_kpis', [])
                report.sentiment_data = extracted_data.get('sentiment', {})
                report.emotion_data = extracted_data.get('emotion', {})
                report.sources_data = extracted_data.get('sources', {})
                report.languages_data = extracted_data.get('languages', {})
                report.topics_data = extracted_data.get('topics', [])
                report.hashtags_data = extracted_data.get('hashtags', [])
                report.influencers_data = extracted_data.get('influencers', [])
                report.reach_breakdown_data = extracted_data.get('reach_breakdown', [])
                report.demographics_data = extracted_data.get('demographics', {})

                # Parse dates
                period = extracted_data.get('period', {})
                if period.get('start'):
                    try:
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

                report.status = 'completed'
                report.save()

                # Add to reports data for merging
                extracted_data['report_id'] = report.id
                extracted_data['source_filename'] = os.path.basename(file_path)
                reports_data.append(extracted_data)

                if extracted_data.get('report_type') not in report_types:
                    report_types.append(extracted_data.get('report_type'))

            except Exception as e:
                logger.error(f"Error processing source report {report.id}: {str(e)}")
                report.status = 'failed'
                report.error_message = str(e)
                report.save()
                # Continue processing other reports

        if not reports_data:
            raise ValueError("Failed to extract data from any source reports")

        # Merge data from all reports
        logger.info(f"Merging data from {len(reports_data)} reports")
        merged_data = merge_multiple_reports(reports_data)
        merged_data['title'] = report_group.title

        # Add manual values if provided
        if report_group.manual_followers:
            if 'presence_passive' not in merged_data:
                merged_data['presence_passive'] = {}
            merged_data['presence_passive']['followers'] = report_group.manual_followers

        if report_group.manual_likes:
            if 'presence_active' not in merged_data:
                merged_data['presence_active'] = {}
            merged_data['presence_active']['likes'] = report_group.manual_likes

        if report_group.manual_shares:
            if 'presence_active' not in merged_data:
                merged_data['presence_active'] = {}
            merged_data['presence_active']['shares'] = report_group.manual_shares

        if report_group.manual_comments:
            if 'presence_active' not in merged_data:
                merged_data['presence_active'] = {}
            merged_data['presence_active']['comments'] = report_group.manual_comments

        if report_group.manual_views:
            if 'presence_passive' not in merged_data:
                merged_data['presence_passive'] = {}
            merged_data['presence_passive']['views'] = report_group.manual_views

        # Store merged data in report group
        report_group.merged_presence_passive = merged_data.get('presence_passive', {})
        report_group.merged_presence_active = merged_data.get('presence_active', {})
        report_group.merged_sentiment = merged_data.get('sentiment', {})
        report_group.merged_emotion = merged_data.get('emotion', {})
        report_group.merged_sources = merged_data.get('sources', {})
        report_group.merged_languages = merged_data.get('languages', {})
        report_group.merged_topics = merged_data.get('topics', [])
        report_group.merged_hashtags = merged_data.get('hashtags', [])
        report_group.merged_influencers = merged_data.get('influencers', [])
        report_group.merged_reach_breakdown = merged_data.get('reach_breakdown', [])
        report_group.merged_demographics = merged_data.get('demographics', {})
        report_group.data_sources = merged_data.get('data_sources', {})
        report_group.included_report_types = report_types

        # Set period from merged data
        period = merged_data.get('period', {})
        if period.get('start'):
            try:
                date_formats = ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d']
                for fmt in date_formats:
                    try:
                        report_group.period_start = datetime.strptime(period['start'], fmt).date()
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
                        report_group.period_end = datetime.strptime(period['end'], fmt).date()
                        break
                    except ValueError:
                        continue
            except:
                pass

        report_group.save()

        # Generate comprehensive Word document
        logger.info(f"Generating merged Word document for report group {group_id}")
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media', 'reports', 'grouped')
        os.makedirs(output_dir, exist_ok=True)

        output_filename = f"merged_report_{group_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        output_path = os.path.join(output_dir, output_filename)

        generate_word_report(merged_data, output_path)

        # Save generated document to model
        with open(output_path, 'rb') as docx_file:
            report_group.generated_docx.save(output_filename, File(docx_file), save=True)

        # Clean up temporary file
        if os.path.exists(output_path):
            os.remove(output_path)

        # Mark as completed
        report_group.status = 'completed'
        report_group.save()

        logger.info(f"Report group {group_id} processed successfully")
        return {'status': 'success', 'group_id': group_id, 'reports_processed': len(reports_data)}

    except ReportGroup.DoesNotExist:
        logger.error(f"Report group {group_id} not found")
        return {'status': 'error', 'message': 'Report group not found'}

    except Exception as e:
        logger.error(f"Error processing report group {group_id}: {str(e)}")

        # Update report group status
        try:
            report_group = ReportGroup.objects.get(id=group_id)
            report_group.status = 'failed'
            report_group.error_message = str(e)
            report_group.save()
        except:
            pass

        # Retry task
        raise self.retry(exc=e, countdown=60)
