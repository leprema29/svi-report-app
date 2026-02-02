"""
PPTX KPI Extraction Service
Extracts surveillance data from monitoring platform PPTX files
"""
import re
from pptx import Presentation
from pptx.util import Inches
from datetime import datetime
from typing import Dict, List, Any


class PPTXKPIExtractor:
    """Extract KPIs from surveillance monitoring PPTX files"""

    def __init__(self, pptx_path: str):
        self.pptx_path = pptx_path
        self.extracted_data = {}

    def extract_all_kpis(self) -> Dict[str, Any]:
        """Main method to extract all KPIs from PPTX"""
        prs = Presentation(self.pptx_path)

        # Extract all text from slides
        full_text = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    full_text += shape.text + "\n"
                # Handle tables
                if shape.has_table:
                    for row in shape.table.rows:
                        for cell in row.cells:
                            full_text += cell.text + "\t"
                        full_text += "\n"

        self.extracted_data = {
            'title': self._extract_title(full_text),
            'period': self._extract_period(full_text),
            'presence_passive': self._extract_presence_passive(full_text),
            'presence_active': self._extract_presence_active(full_text),
            'sentiment': self._extract_sentiment_data(full_text),
            'emotion': self._extract_emotion_data(full_text),
            'sources': self._extract_sources_data(full_text),
            'languages': self._extract_languages_data(full_text),
            'topics': self._extract_topics(full_text),
            'hashtags': self._extract_hashtags(full_text),
            'influencers': self._extract_influencers(full_text),
            # Keep legacy fields for backwards compatibility
            'volume': self._extract_volume_data(full_text),
            'reach': self._extract_reach_data(full_text),
        }

        return self.extracted_data

    def _extract_title(self, text: str) -> str:
        """Extract report title"""
        lines = text.split('\n')
        for line in lines:
            if line.strip():
                return line.strip()
        return "Surveillance Report"

    def _extract_period(self, text: str) -> Dict[str, str]:
        """Extract date period"""
        # Pattern: DD/MM/YYYY to DD/MM/YYYY or various formats
        patterns = [
            r'(\d{2}/\d{2}/\d{4})\s+(?:to|au|à|-)\s+(\d{2}/\d{2}/\d{4})',
            r'(\d{2}\s+\w+\s+\d{4})\s+(?:to|au|à|-)\s+(\d{2}\s+\w+\s+\d{4})',
            r'du\s+(\d{2}/\d{2}/\d{4})\s+au\s+(\d{2}/\d{2}/\d{4})',
            r'période\s*:\s*(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    'start': match.group(1),
                    'end': match.group(2)
                }
        return {'start': '', 'end': ''}

    def _extract_presence_passive(self, text: str) -> Dict[str, Any]:
        """Extract presence passive indicators (followers, views, reach)"""
        data = {
            'followers': 0,
            'followers_evolution': 0.0,
            'views': 0,
            'views_evolution': 0.0,
            'potential_reach': 0,
            'reach_evolution': 0.0
        }

        # Extract followers
        followers_patterns = [
            r'[Ff]ollowers?\s*[:\s]*([0-9,.\s]+)',
            r'[Aa]bonnés?\s*[:\s]*([0-9,.\s]+)',
            r'[Ss]ubscribers?\s*[:\s]*([0-9,.\s]+)',
        ]
        for pattern in followers_patterns:
            match = re.search(pattern, text)
            if match:
                data['followers'] = self._parse_number(match.group(1))
                break

        # Extract followers evolution
        followers_evo_pattern = r'[Ff]ollowers?.*?([+-]?\d+\.?\d*)%'
        match = re.search(followers_evo_pattern, text)
        if match:
            data['followers_evolution'] = float(match.group(1))

        # Extract views/impressions
        views_patterns = [
            r'[Vv]ues?\s*[:\s]*([0-9,.\s]+)',
            r'[Ii]mpressions?\s*[:\s]*([0-9,.\s]+)',
            r'[Vv]iews?\s*[:\s]*([0-9,.\s]+)',
        ]
        for pattern in views_patterns:
            match = re.search(pattern, text)
            if match:
                data['views'] = self._parse_number(match.group(1))
                break

        # Extract views evolution
        views_evo_pattern = r'[Vv]ues?.*?([+-]?\d+\.?\d*)%|[Ii]mpressions?.*?([+-]?\d+\.?\d*)%'
        match = re.search(views_evo_pattern, text)
        if match:
            data['views_evolution'] = float(match.group(1) or match.group(2))

        # Extract potential reach
        reach_patterns = [
            r'[Pp]ortée\s*(?:potentielle)?\s*[:\s]*([0-9,.\s]+)',
            r'[Rr]each\s*[:\s]*([0-9,.\s]+)',
            r'[Pp]otential\s*[Rr]each\s*[:\s]*([0-9,.\s]+)',
        ]
        for pattern in reach_patterns:
            match = re.search(pattern, text)
            if match:
                data['potential_reach'] = self._parse_number(match.group(1))
                break

        # Extract reach evolution
        reach_evo_pattern = r'[Rr]each.*?([+-]?\d+\.?\d*)%|[Pp]ortée.*?([+-]?\d+\.?\d*)%'
        match = re.search(reach_evo_pattern, text)
        if match:
            data['reach_evolution'] = float(match.group(1) or match.group(2) or 0)

        return data

    def _extract_presence_active(self, text: str) -> Dict[str, int]:
        """Extract presence active indicators (comments, likes, shares)"""
        data = {
            'comments': 0,
            'likes': 0,
            'shares': 0
        }

        # Extract comments
        comments_patterns = [
            r'[Cc]ommentaires?\s*[:\s]*([0-9,.\s]+)',
            r'[Cc]omments?\s*[:\s]*([0-9,.\s]+)',
        ]
        for pattern in comments_patterns:
            match = re.search(pattern, text)
            if match:
                data['comments'] = self._parse_number(match.group(1))
                break

        # Extract likes
        likes_patterns = [
            r'[Ll]ikes?\s*[:\s]*([0-9,.\s]+)',
            r"[Jj]'?aime\s*[:\s]*([0-9,.\s]+)",
            r'[Mm]entions?\s*[Jj]\'?aime\s*[:\s]*([0-9,.\s]+)',
        ]
        for pattern in likes_patterns:
            match = re.search(pattern, text)
            if match:
                data['likes'] = self._parse_number(match.group(1))
                break

        # Extract shares
        shares_patterns = [
            r'[Pp]artages?\s*[:\s]*([0-9,.\s]+)',
            r'[Ss]hares?\s*[:\s]*([0-9,.\s]+)',
        ]
        for pattern in shares_patterns:
            match = re.search(pattern, text)
            if match:
                data['shares'] = self._parse_number(match.group(1))
                break

        return data

    def _extract_volume_data(self, text: str) -> Dict[str, Any]:
        """Extract mentions volume and change percentage (legacy)"""
        data = {'mentions': 0, 'change_percent': 0.0}

        # Extract mentions count
        mentions_pattern = r'[Mm]entions?\s*[:\s]*(\d+)'
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
        """Extract reach metrics (legacy)"""
        data = {'reach': 0, 'change_percent': 0.0}

        # Extract reach count
        reach_pattern = r'[Rr]each\s*[:\s]*([\d,.\s]+)'
        reach_match = re.search(reach_pattern, text)
        if reach_match:
            data['reach'] = self._parse_number(reach_match.group(1))

        # Extract reach percentage change
        reach_percent_pattern = r'[Rr]each.*?(-?\d+\.?\d*)%'
        reach_percent_match = re.search(reach_percent_pattern, text)
        if reach_percent_match:
            data['change_percent'] = float(reach_percent_match.group(1))

        return data

    def _extract_sentiment_data(self, text: str) -> Dict[str, int]:
        """Extract sentiment distribution"""
        sentiment_data = {}

        # Pattern variations for sentiment
        patterns = [
            r'[Pp]ositi[fv]e?\s*[:\s]*(\d+)',
            r'[Nn][eé]gati[fv]e?\s*[:\s]*(\d+)',
            r'[Nn]eutr[ea]l?\s*[:\s]*(\d+)',
        ]

        sentiment_names = ['positive', 'negative', 'neutral']

        for pattern, name in zip(patterns, sentiment_names):
            match = re.search(pattern, text)
            if match:
                sentiment_data[name] = int(match.group(1))

        # Alternative pattern: Sentiment (count) percentage
        alt_pattern = r'(Positive|Negative|Neutral|Positif|Négatif|Neutre)\s+(\d+)\s+\([\d.]+%\)'
        matches = re.findall(alt_pattern, text, re.IGNORECASE)

        for sentiment, count in matches:
            key = sentiment.lower()
            if key in ['positif']:
                key = 'positive'
            elif key in ['négatif', 'negatif']:
                key = 'negative'
            elif key in ['neutre']:
                key = 'neutral'
            sentiment_data[key] = int(count)

        return sentiment_data

    def _extract_emotion_data(self, text: str) -> Dict[str, int]:
        """Extract emotion distribution"""
        emotion_data = {}

        emotions = {
            'joy': ['Joy', 'Joie'],
            'neutral': ['Neutral', 'Neutre'],
            'anger': ['Anger', 'Colère'],
            'sadness': ['Sadness', 'Tristesse'],
            'surprise': ['Surprise'],
            'fear': ['Fear', 'Peur'],
            'disgust': ['Disgust', 'Dégoût']
        }

        for emotion_key, emotion_names in emotions.items():
            for name in emotion_names:
                pattern = rf'{name}\s+(\d+)\s*(?:\([\d.]+%\))?'
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    emotion_data[emotion_key] = int(match.group(1))
                    break

        return emotion_data

    def _extract_sources_data(self, text: str) -> Dict[str, int]:
        """Extract sources distribution"""
        sources_data = {}

        platforms = [
            'Facebook', 'Instagram', 'Twitter', 'X', 'TikTok',
            'YouTube', 'LinkedIn', 'WhatsApp', 'Telegram'
        ]

        for platform in platforms:
            pattern = rf'{platform}\s+(\d+)\s*(?:\([\d.]+%\))?'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                sources_data[platform] = int(match.group(1))

        return sources_data

    def _extract_languages_data(self, text: str) -> Dict[str, int]:
        """Extract languages distribution"""
        languages_data = {}

        languages = [
            'French', 'Français', 'English', 'Anglais',
            'Arabic', 'Arabe', 'Spanish', 'Espagnol'
        ]

        for language in languages:
            pattern = rf'{language}\s+(\d+)\s*(?:\([\d.]+%\))?'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Normalize language name
                normalized = language
                if language in ['Français']:
                    normalized = 'French'
                elif language in ['Anglais']:
                    normalized = 'English'
                elif language in ['Arabe']:
                    normalized = 'Arabic'
                elif language in ['Espagnol']:
                    normalized = 'Spanish'
                languages_data[normalized] = int(match.group(1))

        return languages_data

    def _extract_topics(self, text: str) -> List[Dict[str, Any]]:
        """Extract top topics with counts"""
        topics = []

        # Look for topics section
        topics_section = re.search(r'[Tt]opics?.*?(?=[Hh]ashtags?|[Rr]each|$)', text, re.DOTALL)
        if topics_section:
            topic_pattern = r'(\w[\w\s-]+?)\s+(\d+)(?=\s|$)'
            matches = re.findall(topic_pattern, topics_section.group())

            for topic, count in matches[:20]:
                topics.append({
                    'name': topic.strip(),
                    'count': int(count)
                })

        return topics

    def _extract_hashtags(self, text: str) -> List[Dict[str, Any]]:
        """Extract hashtags with counts"""
        hashtags = []

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

        # Look for influencer section with scores
        influencer_pattern = r'([\w\s]+?)\s+(?:https?://[^\s]+\s+)?(\d+)/100'
        matches = re.findall(influencer_pattern, text)

        for name, score in matches:
            influencers.append({
                'name': name.strip(),
                'influence_score': int(score)
            })

        return influencers

    def _parse_number(self, text: str) -> int:
        """Parse number from text, handling various formats"""
        # Remove spaces, commas, and other separators
        cleaned = re.sub(r'[,\s]', '', text.strip())
        try:
            return int(float(cleaned))
        except ValueError:
            return 0


def extract_kpis_from_pptx(pptx_path: str) -> Dict[str, Any]:
    """Convenience function to extract KPIs from PPTX"""
    extractor = PPTXKPIExtractor(pptx_path)
    return extractor.extract_all_kpis()
