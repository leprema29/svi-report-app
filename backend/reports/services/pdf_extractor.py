"""
PDF KPI Extraction Service
Extracts surveillance data from monitoring platform PDFs
"""
import re
import pdfplumber
from datetime import datetime
from typing import Dict, List, Any


class PDFKPIExtractor:
    """Extract KPIs from surveillance monitoring PDFs"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.extracted_data = {}
    
    def extract_all_kpis(self) -> Dict[str, Any]:
        """Main method to extract all KPIs from PDF"""
        with pdfplumber.open(self.pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"
        
        self.extracted_data = {
            'title': self._extract_title(full_text),
            'period': self._extract_period(full_text),
            'volume': self._extract_volume_data(full_text),
            'reach': self._extract_reach_data(full_text),
            'sentiment': self._extract_sentiment_data(full_text),
            'emotion': self._extract_emotion_data(full_text),
            'sources': self._extract_sources_data(full_text),
            'languages': self._extract_languages_data(full_text),
            'topics': self._extract_topics(full_text),
            'hashtags': self._extract_hashtags(full_text),
            'influencers': self._extract_influencers(full_text),
        }
        
        return self.extracted_data
    
    def _extract_title(self, text: str) -> str:
        """Extract report title"""
        lines = text.split('\n')
        # Usually the first non-empty line
        for line in lines:
            if line.strip():
                return line.strip()
        return "Surveillance Report"
    
    def _extract_period(self, text: str) -> Dict[str, str]:
        """Extract date period (e.g., 11/05/2025 to 12/04/2025)"""
        pattern = r'(\d{2}/\d{2}/\d{4})\s+to\s+(\d{2}/\d{2}/\d{4})'
        match = re.search(pattern, text)
        
        if match:
            return {
                'start': match.group(1),
                'end': match.group(2)
            }
        return {'start': '', 'end': ''}
    
    def _extract_volume_data(self, text: str) -> Dict[str, Any]:
        """Extract mentions volume and change percentage"""
        data = {'mentions': 0, 'change_percent': 0.0}
        
        # Extract mentions count
        mentions_pattern = r'Mentions\s+(\d+)'
        mentions_match = re.search(mentions_pattern, text)
        if mentions_match:
            data['mentions'] = int(mentions_match.group(1))
        
        # Extract percentage change
        percent_pattern = r'(-?\d+\.?\d*)%'
        percent_matches = re.findall(percent_pattern, text)
        if percent_matches:
            data['change_percent'] = float(percent_matches[0])
        
        return data
    
    def _extract_reach_data(self, text: str) -> Dict[str, Any]:
        """Extract reach metrics"""
        data = {'reach': 0, 'change_percent': 0.0}
        
        # Extract reach count (handles formats like 10,008,370)
        reach_pattern = r'Reach\s+([\d,]+)'
        reach_match = re.search(reach_pattern, text)
        if reach_match:
            reach_str = reach_match.group(1).replace(',', '')
            data['reach'] = int(reach_str)
        
        # Extract reach percentage change
        reach_percent_pattern = r'Reach\s+[\d,]+\s+(-?\d+\.?\d*)%'
        reach_percent_match = re.search(reach_percent_pattern, text)
        if reach_percent_match:
            data['change_percent'] = float(reach_percent_match.group(1))
        
        return data
    
    def _extract_sentiment_data(self, text: str) -> Dict[str, int]:
        """Extract sentiment distribution"""
        sentiment_data = {}
        
        # Pattern: Positive 147 (57.2%)
        sentiment_pattern = r'(Positive|Negative|Neutral)\s+(\d+)\s+\([\d.]+%\)'
        matches = re.findall(sentiment_pattern, text)
        
        for sentiment, count in matches:
            sentiment_data[sentiment.lower()] = int(count)
        
        return sentiment_data
    
    def _extract_emotion_data(self, text: str) -> Dict[str, int]:
        """Extract emotion distribution"""
        emotion_data = {}
        
        # Pattern: Joy 85 (33.07%)
        emotions = ['Joy', 'Neutral', 'Anger', 'Sadness', 'Surprise', 'Fear', 'Disgust']
        
        for emotion in emotions:
            pattern = rf'{emotion}\s+(\d+)\s+\([\d.]+%\)'
            match = re.search(pattern, text)
            if match:
                emotion_data[emotion.lower()] = int(match.group(1))
        
        return emotion_data
    
    def _extract_sources_data(self, text: str) -> Dict[str, int]:
        """Extract sources distribution"""
        sources_data = {}
        
        # Pattern: Facebook 252 (98.05%)
        platforms = ['Facebook', 'Instagram', 'X \(Twitter\)', 'Videos', 'TikTok', 'YouTube']
        
        for platform in platforms:
            pattern = rf'{platform}\s+(\d+)\s+\([\d.]+%\)'
            match = re.search(pattern, text)
            if match:
                platform_key = platform.replace(' \\', '').replace('\\', '').strip()
                sources_data[platform_key] = int(match.group(1))
        
        return sources_data
    
    def _extract_languages_data(self, text: str) -> Dict[str, int]:
        """Extract languages distribution"""
        languages_data = {}
        
        # Pattern: French 187 (72.76%)
        language_pattern = r'(French|English|Arabic|Spanish)\s+(\d+)\s+\([\d.]+%\)'
        matches = re.findall(language_pattern, text)
        
        for language, count in matches:
            languages_data[language] = int(count)
        
        return languages_data
    
    def _extract_topics(self, text: str) -> List[Dict[str, Any]]:
        """Extract top topics with counts"""
        topics = []
        
        # Look for topics section
        topics_section = re.search(r'Topics.*?(?=Hashtags|Reach|$)', text, re.DOTALL)
        if topics_section:
            # Pattern: rdpc 65
            topic_pattern = r'(\w[\w\s-]+?)\s+(\d+)(?=\s|$)'
            matches = re.findall(topic_pattern, topics_section.group())
            
            for topic, count in matches[:20]:  # Limit to top 20
                topics.append({
                    'name': topic.strip(),
                    'count': int(count)
                })
        
        return topics
    
    def _extract_hashtags(self, text: str) -> List[Dict[str, Any]]:
        """Extract hashtags with counts"""
        hashtags = []
        
        # Pattern: #paulbiya 29
        hashtag_pattern = r'(#\w+)\s+(\d+)'
        matches = re.findall(hashtag_pattern, text)
        
        for hashtag, count in matches:
            hashtags.append({
                'hashtag': hashtag,
                'count': int(count)
            })
        
        return hashtags
    
    def _extract_influencers(self, text: str) -> List[Dict[str, Any]]:
        """Extract top influencers"""
        influencers = []
        
        # Look for influencer section with scores like "47/100"
        influencer_pattern = r'([\w\s]+?)\s+https://[^\s]+\s+(\d+)/100'
        matches = re.findall(influencer_pattern, text)
        
        for name, score in matches:
            influencers.append({
                'name': name.strip(),
                'influence_score': int(score)
            })
        
        return influencers


def extract_kpis_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """Convenience function to extract KPIs from PDF"""
    extractor = PDFKPIExtractor(pdf_path)
    return extractor.extract_all_kpis()
