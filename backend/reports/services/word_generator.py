"""
Word Document Generator Service
Generates formatted Word documents from extracted surveillance data
"""
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from typing import Dict, Any
from datetime import datetime


class WordReportGenerator:
    """Generate Word report from extracted KPI data"""
    
    def __init__(self):
        self.doc = Document()
        self._setup_styles()
    
    def _setup_styles(self):
        """Configure document styles"""
        # Set default font
        style = self.doc.styles['Normal']
        font = style.font
        font.name = 'Arial'
        font.size = Pt(11)
    
    def generate_report(self, data: Dict[str, Any], output_path: str):
        """Generate complete Word report"""
        # Add title
        self._add_title(data.get('title', 'Surveillance Report'))
        
        # Add period
        period = data.get('period', {})
        if period.get('start') and period.get('end'):
            self._add_subtitle(f"Période: {period['start']} - {period['end']}")
        
        self.doc.add_paragraph()  # Spacing
        
        # Add summary section
        self._add_section_heading("1. RÉSUMÉ EXÉCUTIF")
        self._add_summary_table(data)
        
        # Add sentiment analysis
        self._add_section_heading("2. ANALYSE DES SENTIMENTS")
        self._add_sentiment_table(data.get('sentiment', {}))
        
        # Add emotion analysis
        self._add_section_heading("3. ANALYSE DES ÉMOTIONS")
        self._add_emotion_table(data.get('emotion', {}))
        
        # Add sources distribution
        self._add_section_heading("4. RÉPARTITION PAR SOURCE")
        self._add_sources_table(data.get('sources', {}))
        
        # Add languages
        self._add_section_heading("5. RÉPARTITION PAR LANGUE")
        self._add_languages_table(data.get('languages', {}))
        
        # Add topics
        topics = data.get('topics', [])
        if topics:
            self._add_section_heading("6. SUJETS PRINCIPAUX")
            self._add_topics_table(topics)
        
        # Add hashtags
        hashtags = data.get('hashtags', [])
        if hashtags:
            self._add_section_heading("7. HASHTAGS POPULAIRES")
            self._add_hashtags_table(hashtags)
        
        # Add influencers
        influencers = data.get('influencers', [])
        if influencers:
            self._add_section_heading("8. INFLUENCEURS PRINCIPAUX")
            self._add_influencers_table(influencers)
        
        # Save document
        self.doc.save(output_path)
        return output_path
    
    def _add_title(self, title: str):
        """Add main title"""
        heading = self.doc.add_heading(title, 0)
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in heading.runs:
            run.font.color.rgb = RGBColor(0, 51, 102)
    
    def _add_subtitle(self, subtitle: str):
        """Add subtitle"""
        para = self.doc.add_paragraph(subtitle)
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para.runs[0].font.size = Pt(12)
        para.runs[0].font.italic = True
    
    def _add_section_heading(self, heading: str):
        """Add section heading"""
        self.doc.add_paragraph()  # Spacing
        h = self.doc.add_heading(heading, level=1)
        for run in h.runs:
            run.font.color.rgb = RGBColor(31, 78, 120)
    
    def _add_summary_table(self, data: Dict[str, Any]):
        """Add summary KPI table"""
        volume = data.get('volume', {})
        reach = data.get('reach', {})
        
        table = self.doc.add_table(rows=3, cols=3)
        table.style = 'Light Grid Accent 1'
        
        # Header row
        header_cells = table.rows[0].cells
        header_cells[0].text = 'Indicateur'
        header_cells[1].text = 'Valeur'
        header_cells[2].text = 'Variation'
        self._set_cell_background(header_cells[0], 'D5E8F0')
        self._set_cell_background(header_cells[1], 'D5E8F0')
        self._set_cell_background(header_cells[2], 'D5E8F0')
        
        # Volume row
        vol_cells = table.rows[1].cells
        vol_cells[0].text = 'Volume de Mentions'
        vol_cells[1].text = f"{volume.get('mentions', 0):,}"
        change = volume.get('change_percent', 0)
        vol_cells[2].text = f"{change:+.2f}%"
        
        # Reach row
        reach_cells = table.rows[2].cells
        reach_cells[0].text = 'Portée Totale'
        reach_cells[1].text = f"{reach.get('reach', 0):,}"
        reach_change = reach.get('change_percent', 0)
        reach_cells[2].text = f"{reach_change:+.2f}%"
    
    def _add_sentiment_table(self, sentiment_data: Dict[str, int]):
        """Add sentiment distribution table"""
        if not sentiment_data:
            return
        
        total = sum(sentiment_data.values())
        
        table = self.doc.add_table(rows=len(sentiment_data) + 1, cols=3)
        table.style = 'Light Grid Accent 1'
        
        # Header
        header_cells = table.rows[0].cells
        header_cells[0].text = 'Sentiment'
        header_cells[1].text = 'Nombre'
        header_cells[2].text = 'Pourcentage'
        self._set_cell_background(header_cells[0], 'D5E8F0')
        self._set_cell_background(header_cells[1], 'D5E8F0')
        self._set_cell_background(header_cells[2], 'D5E8F0')
        
        # Data rows
        for idx, (sentiment, count) in enumerate(sentiment_data.items(), 1):
            cells = table.rows[idx].cells
            cells[0].text = sentiment.capitalize()
            cells[1].text = str(count)
            percentage = (count / total * 100) if total > 0 else 0
            cells[2].text = f"{percentage:.2f}%"
    
    def _add_emotion_table(self, emotion_data: Dict[str, int]):
        """Add emotion distribution table"""
        if not emotion_data:
            return
        
        total = sum(emotion_data.values())
        
        # Sort by count descending
        sorted_emotions = sorted(emotion_data.items(), key=lambda x: x[1], reverse=True)
        
        table = self.doc.add_table(rows=len(sorted_emotions) + 1, cols=3)
        table.style = 'Light Grid Accent 1'
        
        # Header
        header_cells = table.rows[0].cells
        header_cells[0].text = 'Émotion'
        header_cells[1].text = 'Nombre'
        header_cells[2].text = 'Pourcentage'
        self._set_cell_background(header_cells[0], 'D5E8F0')
        self._set_cell_background(header_cells[1], 'D5E8F0')
        self._set_cell_background(header_cells[2], 'D5E8F0')
        
        # Data rows
        for idx, (emotion, count) in enumerate(sorted_emotions, 1):
            cells = table.rows[idx].cells
            cells[0].text = emotion.capitalize()
            cells[1].text = str(count)
            percentage = (count / total * 100) if total > 0 else 0
            cells[2].text = f"{percentage:.2f}%"
    
    def _add_sources_table(self, sources_data: Dict[str, int]):
        """Add sources distribution table"""
        if not sources_data:
            return
        
        total = sum(sources_data.values())
        
        # Sort by count descending
        sorted_sources = sorted(sources_data.items(), key=lambda x: x[1], reverse=True)
        
        table = self.doc.add_table(rows=len(sorted_sources) + 1, cols=3)
        table.style = 'Light Grid Accent 1'
        
        # Header
        header_cells = table.rows[0].cells
        header_cells[0].text = 'Plateforme'
        header_cells[1].text = 'Mentions'
        header_cells[2].text = 'Pourcentage'
        self._set_cell_background(header_cells[0], 'D5E8F0')
        self._set_cell_background(header_cells[1], 'D5E8F0')
        self._set_cell_background(header_cells[2], 'D5E8F0')
        
        # Data rows
        for idx, (source, count) in enumerate(sorted_sources, 1):
            cells = table.rows[idx].cells
            cells[0].text = source
            cells[1].text = str(count)
            percentage = (count / total * 100) if total > 0 else 0
            cells[2].text = f"{percentage:.2f}%"
    
    def _add_languages_table(self, languages_data: Dict[str, int]):
        """Add languages distribution table"""
        if not languages_data:
            return
        
        total = sum(languages_data.values())
        
        table = self.doc.add_table(rows=len(languages_data) + 1, cols=3)
        table.style = 'Light Grid Accent 1'
        
        # Header
        header_cells = table.rows[0].cells
        header_cells[0].text = 'Langue'
        header_cells[1].text = 'Mentions'
        header_cells[2].text = 'Pourcentage'
        self._set_cell_background(header_cells[0], 'D5E8F0')
        self._set_cell_background(header_cells[1], 'D5E8F0')
        self._set_cell_background(header_cells[2], 'D5E8F0')
        
        # Data rows
        for idx, (language, count) in enumerate(languages_data.items(), 1):
            cells = table.rows[idx].cells
            cells[0].text = language
            cells[1].text = str(count)
            percentage = (count / total * 100) if total > 0 else 0
            cells[2].text = f"{percentage:.2f}%"
    
    def _add_topics_table(self, topics: list):
        """Add top topics table"""
        if not topics:
            return
        
        # Limit to top 15
        topics = topics[:15]
        
        table = self.doc.add_table(rows=len(topics) + 1, cols=3)
        table.style = 'Light Grid Accent 1'
        
        # Header
        header_cells = table.rows[0].cells
        header_cells[0].text = 'Rang'
        header_cells[1].text = 'Sujet'
        header_cells[2].text = 'Mentions'
        self._set_cell_background(header_cells[0], 'D5E8F0')
        self._set_cell_background(header_cells[1], 'D5E8F0')
        self._set_cell_background(header_cells[2], 'D5E8F0')
        
        # Data rows
        for idx, topic in enumerate(topics, 1):
            cells = table.rows[idx].cells
            cells[0].text = str(idx)
            cells[1].text = topic.get('name', '')
            cells[2].text = str(topic.get('count', 0))
    
    def _add_hashtags_table(self, hashtags: list):
        """Add hashtags table"""
        if not hashtags:
            return
        
        # Limit to top 10
        hashtags = hashtags[:10]
        
        table = self.doc.add_table(rows=len(hashtags) + 1, cols=3)
        table.style = 'Light Grid Accent 1'
        
        # Header
        header_cells = table.rows[0].cells
        header_cells[0].text = 'Rang'
        header_cells[1].text = 'Hashtag'
        header_cells[2].text = 'Occurrences'
        self._set_cell_background(header_cells[0], 'D5E8F0')
        self._set_cell_background(header_cells[1], 'D5E8F0')
        self._set_cell_background(header_cells[2], 'D5E8F0')
        
        # Data rows
        for idx, hashtag in enumerate(hashtags, 1):
            cells = table.rows[idx].cells
            cells[0].text = str(idx)
            cells[1].text = hashtag.get('hashtag', '')
            cells[2].text = str(hashtag.get('count', 0))
    
    def _add_influencers_table(self, influencers: list):
        """Add top influencers table"""
        if not influencers:
            return
        
        # Limit to top 10
        influencers = influencers[:10]
        
        table = self.doc.add_table(rows=len(influencers) + 1, cols=3)
        table.style = 'Light Grid Accent 1'
        
        # Header
        header_cells = table.rows[0].cells
        header_cells[0].text = 'Rang'
        header_cells[1].text = 'Influenceur'
        header_cells[2].text = 'Score'
        self._set_cell_background(header_cells[0], 'D5E8F0')
        self._set_cell_background(header_cells[1], 'D5E8F0')
        self._set_cell_background(header_cells[2], 'D5E8F0')
        
        # Data rows
        for idx, influencer in enumerate(influencers, 1):
            cells = table.rows[idx].cells
            cells[0].text = str(idx)
            cells[1].text = influencer.get('name', '')
            cells[2].text = f"{influencer.get('influence_score', 0)}/100"
    
    def _set_cell_background(self, cell, color: str):
        """Set cell background color"""
        shading_elm = OxmlElement('w:shd')
        shading_elm.set(qn('w:fill'), color)
        cell._element.get_or_add_tcPr().append(shading_elm)


def generate_word_report(data: Dict[str, Any], output_path: str) -> str:
    """Convenience function to generate Word report"""
    generator = WordReportGenerator()
    return generator.generate_report(data, output_path)
