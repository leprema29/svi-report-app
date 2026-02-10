"""
PPTX KPI Extraction Service
Extracts surveillance data from Brand24 monitoring platform PPTX files
Supports both Analysis and Demographics report types
"""
import re
from pptx import Presentation
from datetime import datetime
from typing import Dict, List, Any, Optional


class PPTXKPIExtractor:
    """Extract KPIs from Brand24 surveillance monitoring PPTX files"""

    def __init__(self, pptx_path: str):
        self.pptx_path = pptx_path
        self.extracted_data = {}
        self.full_text = ""
        self.slides_text = []
        self.tables = []
        self.report_type = None

    def extract_all_kpis(self) -> Dict[str, Any]:
        """Main method to extract all KPIs from PPTX"""
        prs = Presentation(self.pptx_path)

        # Extract text from all slides
        self.slides_text = []
        self.tables = []

        for slide in prs.slides:
            slide_text = ""
            slide_tables = []

            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    slide_text += shape.text + "\n"

                # Handle tables
                if shape.has_table:
                    table_data = []
                    for row in shape.table.rows:
                        row_data = [cell.text for cell in row.cells]
                        table_data.append(row_data)
                    slide_tables.append(table_data)

            self.slides_text.append(slide_text)
            self.tables.extend(slide_tables)

        self.full_text = "\n".join(self.slides_text)

        # Detect report type
        self.report_type = self._detect_report_type()

        if self.report_type == "brand24_demographics":
            return self._extract_demographics_report()
        else:
            return self._extract_analysis_report()

    def _detect_report_type(self) -> str:
        """Detect whether this is an Analysis or Demographics report"""
        first_slide = self.slides_text[0] if self.slides_text else ""

        if "Demographics" in first_slide or "Gender Distribution" in self.full_text:
            return "brand24_demographics"
        else:
            return "brand24_analysis"

    def _extract_analysis_report(self) -> Dict[str, Any]:
        """Extract data from Brand24 Analysis report"""
        # KPIs available in Analysis report
        available_kpis = [
            "mentions", "reach", "sentiment", "likes", "comments", "shares",
            "sources", "hashtags", "influencers", "presence_score"
        ]
        unavailable_kpis = [
            "demographics", "gender", "age", "countries", "occupation",
            "education", "interests"
        ]

        self.extracted_data = {
            'report_type': 'brand24_analysis',
            'report_type_display': 'Brand24 Analysis Report',
            'available_kpis': available_kpis,
            'unavailable_kpis': unavailable_kpis,
            'title': self._extract_title(),
            'period': self._extract_period(),
            'volume': self._extract_volume_data(),
            'reach': self._extract_reach_data(),
            'presence_passive': self._build_presence_passive(),
            'presence_active': self._extract_presence_active(),
            'sentiment': self._extract_sentiment_data(),
            'emotion': {},  # Not in Brand24 Analysis
            'sources': self._extract_sources_data(),
            'languages': {},  # Not directly in Brand24 Analysis
            'topics': [],  # Not in standard Brand24 Analysis
            'hashtags': self._extract_hashtags(),
            'influencers': self._extract_influencers(),
            'presence_score': self._extract_presence_score(),
            'ave': self._extract_ave(),
        }

        return self.extracted_data

    def _extract_demographics_report(self) -> Dict[str, Any]:
        """Extract data from Brand24 Demographics report"""
        # KPIs available in Demographics report
        available_kpis = [
            "reach", "gender", "age", "countries", "occupation",
            "education", "interests"
        ]
        unavailable_kpis = [
            "mentions", "sentiment", "likes", "comments", "shares",
            "hashtags", "influencers", "presence_score"
        ]

        self.extracted_data = {
            'report_type': 'brand24_demographics',
            'report_type_display': 'Brand24 Demographics Report',
            'available_kpis': available_kpis,
            'unavailable_kpis': unavailable_kpis,
            'title': self._extract_title(),
            'period': self._extract_period(),
            'volume': {'mentions': 0, 'change_percent': 0.0},
            'reach': self._extract_demographics_reach(),
            'presence_passive': {'followers': 0, 'views': 0, 'potential_reach': 0},
            'presence_active': {'comments': 0, 'likes': 0, 'shares': 0},
            'sentiment': {},
            'emotion': {},
            'sources': {},
            'languages': {},
            'topics': [],
            'hashtags': [],
            'influencers': [],
            # Demographics-specific data
            'demographics': {
                'gender': self._extract_gender_distribution(),
                'age': self._extract_age_distribution(),
                'countries': self._extract_countries_distribution(),
                'occupation': self._extract_occupation_distribution(),
                'education': self._extract_education_distribution(),
                'interests': self._extract_interests(),
            }
        }

        return self.extracted_data

    def _extract_title(self) -> str:
        """Extract report title from first slide"""
        if self.slides_text:
            lines = self.slides_text[0].split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) > 3:
                    # Remove " - Analysis" or " - Demographics Report" suffix
                    title = re.sub(r'\s*-\s*(Analysis|Demographics Report).*$', '', line)
                    return title
        return "Surveillance Report"

    def _extract_period(self) -> Dict[str, str]:
        """Extract date period from first slide"""
        if self.slides_text:
            first_slide = self.slides_text[0]

            # Brand24 format: 2025-11-01 - 2025-12-31
            patterns = [
                r'(\d{4}-\d{2}-\d{2})\s*-\s*(\d{4}-\d{2}-\d{2})',
                r'(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})',
            ]

            for pattern in patterns:
                match = re.search(pattern, first_slide)
                if match:
                    return {
                        'start': match.group(1),
                        'end': match.group(2)
                    }

        return {'start': '', 'end': ''}

    def _extract_volume_data(self) -> Dict[str, Any]:
        """Extract mentions volume from Overview slide (slide 3)"""
        data = {'mentions': 0, 'change_percent': 0.0}

        # Look for "Total mentions" followed by number
        pattern = r'Total mentions\s*\n?\s*([\d,]+)\s*\n?\s*([+-]?\d+)%?'
        match = re.search(pattern, self.full_text, re.IGNORECASE)
        if match:
            data['mentions'] = self._parse_number(match.group(1))
            data['change_percent'] = float(match.group(2))

        return data

    def _extract_reach_data(self) -> Dict[str, Any]:
        """Extract reach metrics from Overview slide"""
        data = {'reach': 0, 'change_percent': 0.0}

        # Look for "Total reach" followed by number (handles M for millions, K for thousands)
        pattern = r'Total reach\s*\n?\s*([\d.,]+[MK]?)\s*\n?\s*([+-]?\d+)%?'
        match = re.search(pattern, self.full_text, re.IGNORECASE)
        if match:
            data['reach'] = self._parse_reach_number(match.group(1))
            data['change_percent'] = float(match.group(2))

        return data

    def _build_presence_passive(self) -> Dict[str, Any]:
        """Build presence passive data"""
        reach_data = self._extract_reach_data()

        # Extract social media reach
        social_reach = 0
        pattern = r'Social media reach\s*\n?\s*([\d.,]+[MK]?)'
        match = re.search(pattern, self.full_text, re.IGNORECASE)
        if match:
            social_reach = self._parse_reach_number(match.group(1))

        return {
            'followers': 0,  # Extracted from influencer tables if needed
            'followers_evolution': 0.0,
            'views': 0,
            'views_evolution': 0.0,
            'potential_reach': reach_data.get('reach', 0),
            'reach_evolution': reach_data.get('change_percent', 0.0),
            'social_media_reach': social_reach,
        }

    def _extract_presence_active(self) -> Dict[str, Any]:
        """Extract presence active indicators (comments, likes, shares) from Overview"""
        data = {
            'comments': 0,
            'likes': 0,
            'shares': 0,
            'total_interactions': 0
        }

        # Extract likes (reactions)
        pattern = r'Social media reactions.*?\s*\n?\s*([\d,]+[MK]?)'
        match = re.search(pattern, self.full_text, re.IGNORECASE)
        if match:
            data['likes'] = self._parse_reach_number(match.group(1))

        # Extract comments
        pattern = r'Social media comments\s*\n?\s*([\d,]+)'
        match = re.search(pattern, self.full_text, re.IGNORECASE)
        if match:
            data['comments'] = self._parse_number(match.group(1))

        # Extract shares - only capture first number, not following lines
        pattern = r'Social media shares\s*\n?\s*([\d,]+)'
        match = re.search(pattern, self.full_text, re.IGNORECASE)
        if match:
            data['shares'] = self._parse_number(match.group(1))

        # Extract total interactions
        pattern = r'Total social media interactions\s*\n?\s*([\d,]+[MK]?)'
        match = re.search(pattern, self.full_text, re.IGNORECASE)
        if match:
            data['total_interactions'] = self._parse_reach_number(match.group(1))

        return data

    def _extract_sentiment_data(self) -> Dict[str, int]:
        """Extract sentiment data from Overview"""
        sentiment_data = {}

        # Extract positive mentions
        pattern = r'Positive mentions\s*\n?\s*(\d+)'
        match = re.search(pattern, self.full_text, re.IGNORECASE)
        if match:
            sentiment_data['positive'] = int(match.group(1))

        # Extract negative mentions
        pattern = r'Negative mentions\s*\n?\s*(\d+)'
        match = re.search(pattern, self.full_text, re.IGNORECASE)
        if match:
            sentiment_data['negative'] = int(match.group(1))

        # Calculate neutral (total - positive - negative)
        volume = self._extract_volume_data()
        total = volume.get('mentions', 0)
        positive = sentiment_data.get('positive', 0)
        negative = sentiment_data.get('negative', 0)
        if total > 0:
            sentiment_data['neutral'] = max(0, total - positive - negative)

        return sentiment_data

    def _extract_sources_data(self) -> Dict[str, int]:
        """Extract sources ONLY from 'Most active sites' section/table"""
        sources_data = {}

        # First, check if we have a "Most active sites" slide/section
        most_active_sites_found = False
        for slide_text in self.slides_text:
            if 'Most active sites' in slide_text or 'most active sites' in slide_text.lower():
                most_active_sites_found = True
                break

        if not most_active_sites_found:
            return sources_data

        # Look for the sources table - must have 'Source' header and site domains
        for table in self.tables:
            if len(table) > 1:
                header = table[0] if table else []
                # Only consider tables with 'Source' column header
                if any('Source' in str(cell) for cell in header):
                    for row in table[1:]:
                        if len(row) >= 2:
                            source = row[1] if row[0] == '' else row[0]
                            mentions = row[-1]  # Last column is usually mentions
                            source = source.strip()
                            # Only accept valid site domains (contain a dot)
                            if source and '.' in source and source not in ['', 'Source']:
                                try:
                                    count = self._parse_number(mentions)
                                    if count > 0:
                                        sources_data[source] = count
                                except:
                                    pass

        # Fallback: try regex patterns only for common platforms with .com/.org endings
        if not sources_data:
            platforms = ['x.com', 'youtube.com', 'facebook.com', 'tiktok.com',
                         'instagram.com', 'twitter.com', 'linkedin.com',
                         'actucameroun.com', 'camer.be', 'rfi.fr']
            for platform in platforms:
                pattern = rf'{re.escape(platform)}\s+(\d+)'
                match = re.search(pattern, self.full_text, re.IGNORECASE)
                if match:
                    sources_data[platform] = int(match.group(1))

        return sources_data

    def _extract_hashtags(self) -> List[Dict[str, Any]]:
        """Extract hashtags from table"""
        hashtags = []

        # Look for hashtags table
        for table in self.tables:
            if len(table) > 1:
                header = table[0] if table else []
                if any('Hashtag' in str(cell) for cell in header):
                    for row in table[1:]:
                        if len(row) >= 2:
                            hashtag = row[0]
                            count = row[1]
                            if hashtag and hashtag.startswith('#'):
                                hashtags.append({
                                    'hashtag': hashtag,
                                    'count': self._parse_number(count)
                                })

        # Also try regex
        if not hashtags:
            pattern = r'(#[\w]+)\s+(\d+)'
            matches = re.findall(pattern, self.full_text)
            for hashtag, count in matches:
                hashtags.append({
                    'hashtag': hashtag,
                    'count': int(count)
                })

        return hashtags[:15]

    def _extract_influencers(self) -> List[Dict[str, Any]]:
        """Extract influencers from tables"""
        influencers = []

        # Look for influencer tables
        for table in self.tables:
            if len(table) > 1:
                header = table[0] if table else []
                if any('Profile name' in str(cell) or 'Influencer' in str(cell) for cell in header):
                    for row in table[1:]:
                        if len(row) >= 3:
                            # Parse profile name (may contain platform)
                            profile = row[1] if row[0] == '' else row[0]
                            profile_parts = profile.split('\n')
                            name = profile_parts[0].strip()
                            platform = profile_parts[1].strip() if len(profile_parts) > 1 else ''

                            # Get other metrics
                            mentions = 0
                            reach = 0
                            followers = 0
                            score = 0

                            for i, cell in enumerate(row):
                                cell_str = str(cell).strip()
                                if i > 0 and cell_str.isdigit():
                                    if mentions == 0:
                                        mentions = int(cell_str)
                                    elif 'K' in str(row[i]) or 'M' in str(row[i]):
                                        reach = self._parse_reach_number(cell_str)

                            # Check for follower count
                            if 'Followers' in str(header):
                                followers_idx = next((i for i, h in enumerate(header) if 'Followers' in str(h)), -1)
                                if followers_idx > 0 and followers_idx < len(row):
                                    followers = self._parse_reach_number(row[followers_idx])

                            # Check for score
                            if 'Score' in str(header):
                                score_idx = next((i for i, h in enumerate(header) if 'Score' in str(h)), -1)
                                if score_idx > 0 and score_idx < len(row):
                                    try:
                                        score = int(row[score_idx])
                                    except:
                                        score = 0

                            if name and name not in ['', 'Profile name']:
                                influencers.append({
                                    'name': name,
                                    'platform': platform,
                                    'mentions': mentions,
                                    'reach': reach,
                                    'followers': followers,
                                    'influence_score': score
                                })

        # Remove duplicates by name (keep first occurrence)
        seen_names = set()
        unique_influencers = []
        for inf in influencers:
            name_lower = inf['name'].lower()
            if name_lower not in seen_names:
                seen_names.add(name_lower)
                unique_influencers.append(inf)

        return unique_influencers[:15]

    def _extract_presence_score(self) -> Dict[str, Any]:
        """Extract presence score"""
        data = {'score': 0, 'percentile': 0}

        # Look for presence score
        pattern = r'(?:Current\s+)?Presence Score\s*\n?\s*(\d+)'
        match = re.search(pattern, self.full_text, re.IGNORECASE)
        if match:
            data['score'] = int(match.group(1))

        # Look for percentile
        pattern = r'higher than (\d+)% of brands'
        match = re.search(pattern, self.full_text, re.IGNORECASE)
        if match:
            data['percentile'] = int(match.group(1))

        return data

    def _extract_ave(self) -> Dict[str, Any]:
        """Extract AVE (Advertising Value Equivalent)"""
        data = {'value': 0, 'currency': 'USD'}

        pattern = r'AVE\s*\n?\s*\$?([\d,]+[MK]?)'
        match = re.search(pattern, self.full_text, re.IGNORECASE)
        if match:
            data['value'] = self._parse_reach_number(match.group(1))

        return data

    # Demographics extraction methods
    def _extract_demographics_reach(self) -> Dict[str, Any]:
        """Extract reach from demographics report"""
        data = {'reach': 0, 'change_percent': 0.0}

        pattern = r'Total Reach\s*\n?\s*([\d,]+[MK]?)'
        match = re.search(pattern, self.full_text, re.IGNORECASE)
        if match:
            data['reach'] = self._parse_reach_number(match.group(1))

        return data

    def _extract_gender_distribution(self) -> Dict[str, float]:
        """Extract gender distribution"""
        data = {}

        pattern = r'Female:\s*([\d.]+)%'
        match = re.search(pattern, self.full_text, re.IGNORECASE)
        if match:
            data['female'] = float(match.group(1))

        pattern = r'Male:\s*([\d.]+)%'
        match = re.search(pattern, self.full_text, re.IGNORECASE)
        if match:
            data['male'] = float(match.group(1))

        return data

    def _extract_age_distribution(self) -> List[Dict[str, Any]]:
        """Extract age distribution"""
        age_data = []

        age_groups = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+']
        for age_group in age_groups:
            # Pattern: age group followed by percentage and count
            pattern = rf'{re.escape(age_group)}\s*\n?\s*([\d.]+)%\s*\(([\d,\s]+)\)'
            matches = re.findall(pattern, self.full_text)
            for percent, count in matches:
                age_data.append({
                    'age_group': age_group,
                    'percentage': float(percent),
                    'count': self._parse_number(count)
                })

        return age_data

    def _extract_countries_distribution(self) -> List[Dict[str, Any]]:
        """Extract countries distribution from table"""
        countries = []

        for table in self.tables:
            if len(table) > 1:
                header = table[0] if table else []
                if any('Country' in str(cell) for cell in header):
                    for row in table[1:]:
                        if len(row) >= 2:
                            country = row[0]
                            reach_info = row[1]

                            # Clean country name (remove emoji)
                            country = re.sub(r'[^\w\s]', '', country).strip()

                            # Parse reach percentage and value
                            match = re.search(r'([\d.]+)%\s*\(([\d,\sKM]+)\)', reach_info)
                            if match and country:
                                countries.append({
                                    'country': country,
                                    'percentage': float(match.group(1)),
                                    'reach': self._parse_reach_number(match.group(2))
                                })

        return countries[:15]

    def _extract_occupation_distribution(self) -> List[Dict[str, Any]]:
        """Extract occupation distribution"""
        occupations = []

        occupation_types = [
            'Full-time work', 'Part-time work', 'Unemployed', 'Studies',
            'Homemaker', 'Retired', 'Own business', 'Leave of absence', 'Parental leave'
        ]

        for occupation in occupation_types:
            pattern = rf'{re.escape(occupation)}\s*\n?\s*([\d.]+)%\s*\(([\d,\s]+)\)'
            match = re.search(pattern, self.full_text, re.IGNORECASE)
            if match:
                occupations.append({
                    'occupation': occupation,
                    'percentage': float(match.group(1)),
                    'count': self._parse_number(match.group(2))
                })

        return occupations

    def _extract_education_distribution(self) -> List[Dict[str, Any]]:
        """Extract education level distribution"""
        education = []

        education_levels = ['University', 'School', 'Postgraduate', 'None completed']

        for level in education_levels:
            pattern = rf'{re.escape(level)}\s*\n?\s*([\d.]+)%\s*\(([\d,\s]+)\)'
            match = re.search(pattern, self.full_text, re.IGNORECASE)
            if match:
                education.append({
                    'level': level,
                    'percentage': float(match.group(1)),
                    'count': self._parse_number(match.group(2))
                })

        return education

    def _extract_interests(self) -> List[Dict[str, Any]]:
        """Extract interests"""
        interests = []

        # Pattern: emoji + interest name + percentage
        pattern = r'[^\w\s]?\s*([A-Za-z\s]+)\s*\n?\s*([\d.]+)%\s*\(([\d,\sKM]+)\)'
        matches = re.findall(pattern, self.full_text)

        for interest, percent, count in matches:
            interest = interest.strip()
            if interest and len(interest) > 2:
                interests.append({
                    'interest': interest,
                    'percentage': float(percent),
                    'reach': self._parse_reach_number(count)
                })

        return interests[:10]

    def _parse_number(self, text: str) -> int:
        """Parse number from text, handling various formats"""
        if not text:
            return 0
        cleaned = re.sub(r'[,\s]', '', str(text).strip())
        try:
            return int(float(cleaned))
        except ValueError:
            return 0

    def _parse_reach_number(self, text: str) -> int:
        """Parse reach number handling K and M suffixes"""
        if not text:
            return 0
        text = str(text).strip().upper()
        text = re.sub(r'[,\s]', '', text)

        multiplier = 1
        if text.endswith('K'):
            multiplier = 1000
            text = text[:-1]
        elif text.endswith('M'):
            multiplier = 1000000
            text = text[:-1]

        try:
            return int(float(text) * multiplier)
        except ValueError:
            return 0


def extract_kpis_from_pptx(pptx_path: str) -> Dict[str, Any]:
    """Convenience function to extract KPIs from Brand24 PPTX"""
    extractor = PPTXKPIExtractor(pptx_path)
    return extractor.extract_all_kpis()
