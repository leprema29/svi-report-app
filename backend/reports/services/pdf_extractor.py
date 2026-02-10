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
        "mentions", "reach", "reach_breakdown", "sentiment", "emotions",
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
            'reach_breakdown': self._extract_reach_breakdown(),
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
        Extract emotion distribution from the Emotion section - Mention format:
        Joy
        85 (33.07%)
        """
        emotion_data = {}

        # Find the Emotion section specifically (to avoid matching Sentiment's "Neutral")
        emotion_section = re.search(
            r'Emotion\s+\d+/\d+/\d+\s+to\s+\d+/\d+/\d+.*?(?=Languages|Countries|Topics|$)',
            self.full_text,
            re.DOTALL | re.IGNORECASE
        )

        search_text = emotion_section.group() if emotion_section else self.full_text

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
                match = re.search(pattern, search_text, re.IGNORECASE)
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
        Extract topics from the bar chart section on page 5.
        Format: Numbers column first, then topic names column.
        Handles merged numbers like "2221" (22, 21) and "1010" (10, 10).
        """
        topics = []

        # Find the Topics bar chart section (on page 5)
        topics_section = re.search(
            r'Topics\s+\d+/\d+/\d+\s+to\s+\d+/\d+/\d+\s+\([^)]+\)\s*\n([\s\S]*?)(?=Reach\s+\([^)]+\)|$)',
            self.full_text,
            re.IGNORECASE
        )

        if topics_section:
            section_text = topics_section.group(1)
            lines = section_text.split('\n')

            # Collect all numbers, handling merged cases
            numbers = []
            topic_names = []
            found_first_topic = False

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Check if line is pure number(s)
                if line.isdigit():
                    num = int(line)
                    # Check for merged numbers (4 digits that are likely 2 two-digit numbers)
                    if len(line) == 4 and num > 99:
                        # Could be merged like "2221" -> 22, 21 or "1010" -> 10, 10
                        first = int(line[:2])
                        second = int(line[2:])
                        # Validate: bar chart values decrease, so first >= second usually
                        if first >= second and first <= 99 and second <= 99:
                            numbers.append(first)
                            numbers.append(second)
                        else:
                            numbers.append(num)
                    else:
                        numbers.append(num)

                # Check if number attached to first topic (e.g., "6rdpc")
                elif re.match(r'^(\d+)([a-zA-ZÀ-ÿ])', line):
                    match = re.match(r'^(\d+)([a-zA-ZÀ-ÿ].*)', line)
                    if match:
                        numbers.append(int(match.group(1)))
                        found_first_topic = True
                        topic = match.group(2).strip('…').strip()
                        if topic and len(topic) > 1:
                            topic_names.append(topic)

                # Topic name (starts with letter)
                elif re.match(r'^[a-zA-ZÀ-ÿ\']', line) and not line.startswith('http'):
                    found_first_topic = True
                    topic = line.strip('…').strip()
                    if topic and len(topic) > 1:
                        topic_names.append(topic)

            # Match numbers with topic names
            for i, topic in enumerate(topic_names):
                count = numbers[i] if i < len(numbers) else 0
                topics.append({
                    'name': topic,
                    'count': count
                })

        # Remove duplicates and sort by count
        seen = set()
        unique_topics = []
        for t in topics:
            name_lower = t['name'].lower()
            if name_lower not in seen and len(t['name']) > 1:
                seen.add(name_lower)
                unique_topics.append(t)

        unique_topics.sort(key=lambda x: x['count'], reverse=True)
        return unique_topics[:20]

    def _extract_hashtags(self) -> List[Dict[str, Any]]:
        """
        Extract hashtags - Mention format has numbers column then hashtags column:
        29
        27
        13
        ...
        #paulbiya
        #biya2025
        #cameroon
        ...
        """
        hashtags = []

        # Find Hashtags section (on page 4)
        hashtags_section = re.search(
            r'Hashtags\s+\d+/\d+/\d+\s+to\s+\d+/\d+/\d+.*?(?=Candidat|Topics\s+\d+/\d+/\d+|Reach|Influence|$)',
            self.full_text,
            re.DOTALL | re.IGNORECASE
        )

        if hashtags_section:
            section_text = hashtags_section.group()

            # Extract all numbers (counts) from the section
            numbers = re.findall(r'^(\d+)$', section_text, re.MULTILINE)

            # Extract all hashtags from the section
            hashtag_names = re.findall(r'(#[\w]+)', section_text)

            # Match numbers with hashtags (they appear in order)
            for i, hashtag in enumerate(hashtag_names):
                count = int(numbers[i]) if i < len(numbers) else 1
                hashtags.append({
                    'hashtag': hashtag,
                    'count': count
                })

        # Fallback: try direct pattern matching if above didn't work
        if not hashtags:
            # Pattern: count followed by hashtag on next line
            pattern = r'(\d+)\s*\n\s*(#[\w]+)'
            matches = re.findall(pattern, self.full_text)
            for count, hashtag in matches:
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
        Extract influencers from 'Influence - Top mentions Facebook' section:
        Médiatude
        https://www.facebook.com/profile.php?
        47/100
        """
        influencers = []

        # Find the "Influence - Top mentions Facebook" section
        influence_section = re.search(
            r'Influence\s*-\s*Top\s+mentions\s+Fac[^\n]*\n([\s\S]*?)(?=Influence\s*-\s*Top|$)',
            self.full_text,
            re.IGNORECASE
        )

        if influence_section:
            section_text = influence_section.group(1)

            # Pattern: Name followed by URL (with profile.php) followed by score/100
            # The URL may be truncated so we look for facebook.com/profile
            pattern = r'([A-Za-z0-9À-ÿ\s\'\'-]+?)\s*\n?\s*https://www\.facebook\.com/profile[^\n]*\n?\s*(\d+)/100'
            matches = re.findall(pattern, section_text, re.IGNORECASE)

            for name, score in matches:
                name = name.strip()
                # Filter out noise like page numbers, dates
                if (name and
                    len(name) > 2 and
                    not re.match(r'^\d+$', name) and
                    not re.match(r'\d+/\d+/\d+', name) and
                    name.lower() not in ['document', 'page', 'candidat']):
                    influencers.append({
                        'name': name,
                        'influence_score': int(score),
                        'platform': 'Facebook'
                    })

        # Fallback: try a simpler pattern if above didn't work
        if not influencers:
            pattern = r'([A-Za-z0-9À-ÿ\s\'\'-]{3,}?)\s*\n\s*https://[^\s]+\s*\n?\s*(\d+)/100'
            matches = re.findall(pattern, self.full_text)
            for name, score in matches:
                name = name.strip()
                if name and len(name) > 2 and not name.isdigit():
                    influencers.append({
                        'name': name,
                        'influence_score': int(score),
                        'platform': 'Facebook'
                    })

        return influencers[:15]

    def _extract_reach_breakdown(self) -> List[Dict[str, Any]]:
        """
        Extract reach breakdown (top posts with their reach) from Mention format:
        Médiatude
        https://www.facebook.com/photo/?fbid=12741620214
        08859&set=a.592433216248413698.3KReach
        (URL spans multiple lines, reach value like "698.3K" at end followed by 'Reach')
        """
        reach_posts = []

        # Find lines ending with reach values (e.g., "698.3KReach", "497.8KReach")
        # The reach value pattern is: digits, optional decimal, optional K/M/B, then "Reach"
        # We need to capture ONLY the actual reach value, not URL fragments
        # Real reach values are like: 698.3K, 560.5K, 497.8K (relatively small numbers with K/M suffix)

        lines = self.full_text.split('\n')
        current_name = None

        for i, line in enumerate(lines):
            line = line.strip()

            # If line is a name (starts with letter, not a URL, not too long)
            if (line and
                re.match(r'^[A-Za-zÀ-ÿ]', line) and
                not line.startswith('http') and
                len(line) < 100 and
                'facebook.com' not in line.lower() and
                not re.search(r'\d+/\d+/\d+', line)):  # Not a date
                current_name = line

            # If line ends with reach value pattern (e.g., "698.3KReach")
            # Real reach values are like 698.3K, 560.5K, 497.8K (1-3 digits, decimal, 1 digit, K/M)
            # The decimal point distinguishes reach values from URL numbers
            reach_match = re.search(r'(\d{1,3}\.\d[KMB])Reach\s*$', line, re.IGNORECASE)
            if reach_match and current_name:
                reach_value = reach_match.group(1)
                reach_num = self._parse_reach_value(reach_value)

                # Avoid duplicates
                if not any(p['name'] == current_name and p['reach'] == reach_num for p in reach_posts):
                    reach_posts.append({
                        'name': current_name,
                        'reach': reach_num,
                        'reach_display': reach_value
                    })

                current_name = None  # Reset for next entry

        return reach_posts[:10]

    def _parse_reach_value(self, value: str) -> int:
        """Parse reach value like 698.3K, 1.2M to integer"""
        value = value.strip().upper()
        multiplier = 1
        if value.endswith('K'):
            multiplier = 1000
            value = value[:-1]
        elif value.endswith('M'):
            multiplier = 1000000
            value = value[:-1]
        elif value.endswith('B'):
            multiplier = 1000000000
            value = value[:-1]

        try:
            return int(float(value) * multiplier)
        except ValueError:
            return 0

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
