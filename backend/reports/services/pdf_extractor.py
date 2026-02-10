"""
PDF KPI Extraction Service
Extracts surveillance data from Mention.com monitoring platform PDFs
"""
import re
from datetime import datetime
from typing import Dict, List, Any

# Use PyPDF2 as it's more reliable across environments
from PyPDF2 import PdfReader


class PDFKPIExtractor:
    """Extract KPIs from Mention.com surveillance monitoring PDFs"""

    # Report type identifier
    REPORT_TYPE = "mention_dashboard"
    REPORT_TYPE_DISPLAY = "Mention.com Dashboard"

    # KPIs available in this report type
    AVAILABLE_KPIS = [
        "mentions", "reach", "sentiment", "emotions",
        "sources", "languages", "topics", "hashtags", "influencers"
    ]

    # KPIs NOT available in this report type
    UNAVAILABLE_KPIS = [
        "followers", "views", "comments", "likes", "shares",
        "demographics", "gender", "age", "countries"
    ]

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.extracted_data = {}
        self.full_text = ""

    def extract_all_kpis(self) -> Dict[str, Any]:
        """Main method to extract all KPIs from Mention.com PDF"""
        # Extract text from PDF
        reader = PdfReader(self.pdf_path)
        self.full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.full_text += text + "\n"

        self.extracted_data = {
            'report_type': self.REPORT_TYPE,
            'report_type_display': self.REPORT_TYPE_DISPLAY,
            'available_kpis': self.AVAILABLE_KPIS,
            'unavailable_kpis': self.UNAVAILABLE_KPIS,
            'title': self._extract_title(),
            'period': self._extract_period(),
            'volume': self._extract_volume_data(),
            'reach': self._extract_reach_data(),
            'presence_passive': self._build_presence_passive(),
            'presence_active': self._build_presence_active(),  # Not available in Mention
            'sentiment': self._extract_sentiment_data(),
            'emotion': self._extract_emotion_data(),
            'sources': self._extract_sources_data(),
            'languages': self._extract_languages_data(),
            'topics': self._extract_topics(),
            'hashtags': self._extract_hashtags(),
            'influencers': self._extract_influencers(),
        }

        return self.extracted_data

    def _extract_title(self) -> str:
        """Extract report title (first non-empty line)"""
        lines = self.full_text.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('Document') and len(line) > 3:
                return line
        return "Surveillance Report"

    def _extract_period(self) -> Dict[str, str]:
        """Extract date period - Mention format: 11/05/2025 to 12/04/2025"""
        patterns = [
            r'(\d{2}/\d{2}/\d{4})\s+to\s+(\d{2}/\d{2}/\d{4})',
            r'(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})',
            r'(\d{2}/\d{2}/\d{4})\s+au\s+(\d{2}/\d{2}/\d{4})',
        ]

        for pattern in patterns:
            match = re.search(pattern, self.full_text, re.IGNORECASE)
            if match:
                return {
                    'start': match.group(1),
                    'end': match.group(2)
                }
        return {'start': '', 'end': ''}

    def _extract_volume_data(self) -> Dict[str, Any]:
        """
        Extract mentions volume - Mention format:
        Mentions
        257
        -92.74%
        """
        data = {'mentions': 0, 'change_percent': 0.0}

        # Pattern: Mentions followed by number on next line
        pattern = r'Mentions\s*\n\s*(\d+)\s*\n\s*(-?\d+\.?\d*)%'
        match = re.search(pattern, self.full_text)
        if match:
            data['mentions'] = int(match.group(1))
            data['change_percent'] = float(match.group(2))
        else:
            # Fallback: just find Mentions followed by a number
            fallback = r'Mentions\s+(\d+)'
            match = re.search(fallback, self.full_text)
            if match:
                data['mentions'] = int(match.group(1))

        return data

    def _extract_reach_data(self) -> Dict[str, Any]:
        """
        Extract reach metrics - Mention format:
        Reach
        10,008,370
        -98.65%
        """
        data = {'reach': 0, 'change_percent': 0.0}

        # Pattern: Reach followed by number (with commas) on next line
        pattern = r'Reach\s*\n\s*([\d,]+)\s*\n\s*(-?\d+\.?\d*)%'
        match = re.search(pattern, self.full_text)
        if match:
            reach_str = match.group(1).replace(',', '')
            data['reach'] = int(reach_str)
            data['change_percent'] = float(match.group(2))
        else:
            # Fallback pattern
            fallback = r'Reach\s+([\d,]+)'
            match = re.search(fallback, self.full_text)
            if match:
                reach_str = match.group(1).replace(',', '')
                data['reach'] = int(reach_str)

        return data

    def _build_presence_passive(self) -> Dict[str, Any]:
        """Build presence passive data from available metrics"""
        reach_data = self._extract_reach_data()
        return {
            'followers': 0,  # Not available in Mention dashboard
            'followers_evolution': 0.0,
            'views': 0,  # Not available in Mention dashboard
            'views_evolution': 0.0,
            'potential_reach': reach_data.get('reach', 0),
            'reach_evolution': reach_data.get('change_percent', 0.0)
        }

    def _build_presence_active(self) -> Dict[str, int]:
        """Presence active data - NOT available in Mention dashboard PDF"""
        return {
            'comments': 0,
            'likes': 0,
            'shares': 0,
            '_note': 'Not available in Mention Dashboard reports. Use Brand24 Analysis reports for this data.'
        }

    def _extract_sentiment_data(self) -> Dict[str, int]:
        """
        Extract sentiment distribution - Mention format:
        Positive
        147 (57.2%)
        """
        sentiment_data = {}

        sentiments = {
            'positive': ['Positive', 'Positif'],
            'negative': ['Negative', 'Négatif', 'Negatif'],
            'neutral': ['Neutral', 'Neutre']
        }

        for key, names in sentiments.items():
            for name in names:
                # Pattern: Sentiment name followed by "count (percent%)"
                pattern = rf'{name}\s*\n?\s*(\d+)\s*\([\d.]+%\)'
                match = re.search(pattern, self.full_text, re.IGNORECASE)
                if match:
                    sentiment_data[key] = int(match.group(1))
                    break

        return sentiment_data

    def _extract_emotion_data(self) -> Dict[str, int]:
        """
        Extract emotion distribution - Mention format:
        Joy
        85 (33.07%)
        """
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

        for key, names in emotions.items():
            for name in names:
                pattern = rf'{name}\s*\n?\s*(\d+)\s*\([\d.]+%\)'
                match = re.search(pattern, self.full_text, re.IGNORECASE)
                if match:
                    emotion_data[key] = int(match.group(1))
                    break

        return emotion_data

    def _extract_sources_data(self) -> Dict[str, int]:
        """
        Extract sources distribution ONLY from 'Sources' section - Mention format:
        Sources (Candidat Paul Bi…
        Facebook
        252 (98.05%)
        """
        sources_data = {}

        # Find the Sources section
        sources_section = re.search(
            r'Sources\s*(?:\([^)]+\))?\s*[\d/]+\s*to\s*[\d/]+.*?(?=Sentiment|Emotion|Languages|$)',
            self.full_text,
            re.DOTALL | re.IGNORECASE
        )

        # Only search within Sources section, or use full text as fallback
        search_text = sources_section.group() if sources_section else self.full_text

        # Only look for social media platforms (not websites or hashtags)
        platforms = [
            'Facebook', 'Instagram', 'Twitter', 'X', 'TikTok',
            'YouTube', 'LinkedIn', 'Videos', 'Web', 'News', 'Blogs'
        ]

        for platform in platforms:
            # Pattern: Platform name followed by "count (percent%)"
            # Handle "X (Twitter)" case
            if platform == 'X':
                pattern = r'X\s*\(Twitter\)\s*\n?\s*(\d+)\s*\([\d.]+%\)'
            else:
                pattern = rf'{platform}\s*\n?\s*(\d+)\s*\([\d.]+%\)'

            match = re.search(pattern, search_text, re.IGNORECASE)
            if match:
                sources_data[platform] = int(match.group(1))

        return sources_data

    def _extract_languages_data(self) -> Dict[str, int]:
        """
        Extract languages distribution - Mention format:
        French
        187 (72.76%)
        """
        languages_data = {}

        languages = {
            'French': ['French', 'Français'],
            'English': ['English', 'Anglais'],
            'Arabic': ['Arabic', 'Arabe'],
            'Spanish': ['Spanish', 'Espagnol'],
            'German': ['German', 'Allemand'],
            'Portuguese': ['Portuguese', 'Portugais'],
        }

        for normalized, names in languages.items():
            for name in names:
                pattern = rf'{name}\s*\n?\s*(\d+)\s*\([\d.]+%\)'
                match = re.search(pattern, self.full_text, re.IGNORECASE)
                if match:
                    languages_data[normalized] = int(match.group(1))
                    break

        return languages_data

    def _extract_topics(self) -> List[Dict[str, Any]]:
        """
        Extract topics - Mention format shows count before topic name:
        65
        rdpc
        or in word cloud format
        """
        topics = []

        # Find Topics section
        topics_section = re.search(
            r'Topics.*?(?=Hashtags|Reach|Influence|$)',
            self.full_text,
            re.DOTALL | re.IGNORECASE
        )

        if topics_section:
            section_text = topics_section.group()

            # Pattern 1: number followed by topic name (from bar chart)
            pattern1 = r'(\d+)\s*\n\s*([a-zA-Zàâäéèêëïîôùûüç\s-]+?)(?=\d|\n\n|$)'
            matches = re.findall(pattern1, section_text)

            for count, topic in matches:
                topic = topic.strip()
                if topic and len(topic) > 1 and not topic.isdigit():
                    topics.append({
                        'name': topic,
                        'count': int(count)
                    })

        # Remove duplicates and sort by count
        seen = set()
        unique_topics = []
        for t in topics:
            if t['name'].lower() not in seen:
                seen.add(t['name'].lower())
                unique_topics.append(t)

        unique_topics.sort(key=lambda x: x['count'], reverse=True)
        return unique_topics[:20]

    def _extract_hashtags(self) -> List[Dict[str, Any]]:
        """
        Extract hashtags - Mention format:
        29
        #paulbiya
        or
        #paulbiya 29
        """
        hashtags = []

        # Find Hashtags section
        hashtags_section = re.search(
            r'Hashtags.*?(?=Topics|Reach|Influence|Countries|$)',
            self.full_text,
            re.DOTALL | re.IGNORECASE
        )

        if hashtags_section:
            section_text = hashtags_section.group()

            # Pattern 1: count followed by hashtag
            pattern1 = r'(\d+)\s*\n?\s*(#[\w]+)'
            matches1 = re.findall(pattern1, section_text)

            for count, hashtag in matches1:
                hashtags.append({
                    'hashtag': hashtag,
                    'count': int(count)
                })

            # Pattern 2: hashtag followed by count
            if not hashtags:
                pattern2 = r'(#[\w]+)\s+(\d+)'
                matches2 = re.findall(pattern2, section_text)
                for hashtag, count in matches2:
                    hashtags.append({
                        'hashtag': hashtag,
                        'count': int(count)
                    })

        # Remove duplicates and sort
        seen = set()
        unique_hashtags = []
        for h in hashtags:
            if h['hashtag'].lower() not in seen:
                seen.add(h['hashtag'].lower())
                unique_hashtags.append(h)

        unique_hashtags.sort(key=lambda x: x['count'], reverse=True)
        return unique_hashtags[:15]

    def _extract_influencers(self) -> List[Dict[str, Any]]:
        """
        Extract influencers - Mention format:
        Name
        https://url
        47/100
        """
        influencers = []

        # Pattern: Name followed by URL followed by score/100
        pattern = r'([A-Za-z0-9\s\'-]+?)\s*\n\s*https://[^\s]+\s*\n?\s*(\d+)/100'
        matches = re.findall(pattern, self.full_text)

        for name, score in matches:
            name = name.strip()
            if name and len(name) > 2:
                influencers.append({
                    'name': name,
                    'influence_score': int(score),
                    'platform': 'facebook.com'  # Default for Mention
                })

        return influencers[:15]

    def _parse_number(self, text: str) -> int:
        """Parse number from text, handling various formats"""
        cleaned = re.sub(r'[,\s]', '', text.strip())
        try:
            return int(float(cleaned))
        except ValueError:
            return 0


def extract_kpis_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """Convenience function to extract KPIs from Mention.com PDF"""
    extractor = PDFKPIExtractor(pdf_path)
    return extractor.extract_all_kpis()
