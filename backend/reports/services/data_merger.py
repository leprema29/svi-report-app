"""
Data Merger Service

Combines data from multiple surveillance reports into a unified dataset.
Tracks data sources for reference section in generated reports.
"""
import os
from typing import Dict, List, Any, Optional
from collections import defaultdict


class DataMerger:
    """Merges data from multiple surveillance reports"""

    def __init__(self):
        self.data_sources = defaultdict(list)  # Track which data came from which report
        self.merged_data = {}

    def merge_reports(self, reports_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge data from multiple reports into a unified dataset.

        Args:
            reports_data: List of dictionaries containing extracted data from each report.
                         Each dict should include 'source_filename', 'source_type', 'report_id'

        Returns:
            Dictionary with merged data and source references
        """
        self.data_sources = defaultdict(list)
        self.merged_data = {
            'title': '',
            'period': {'start': None, 'end': None},
            'presence_passive': {},
            'presence_active': {},
            'volume': {},
            'reach': {},
            'sentiment': {},
            'emotion': {},
            'sources': {},
            'languages': {},
            'topics': [],
            'hashtags': [],
            'influencers': [],
            'reach_breakdown': [],
            'demographics': {},
            'report_types': [],
            'source_files': [],
            'data_sources': {}
        }

        for report_data in reports_data:
            self._merge_single_report(report_data)

        # Deduplicate and finalize
        self._finalize_merged_data()
        self.merged_data['data_sources'] = dict(self.data_sources)

        return self.merged_data

    def _merge_single_report(self, report_data: Dict[str, Any]):
        """Merge a single report's data into the combined dataset"""
        source_info = {
            'report_id': report_data.get('report_id'),
            'filename': report_data.get('source_filename', 'Unknown'),
            'report_type': report_data.get('report_type', 'unknown'),
            'report_type_display': report_data.get('report_type_display', '')
        }

        # Track source file
        if source_info['filename'] not in [f['filename'] for f in self.merged_data['source_files']]:
            self.merged_data['source_files'].append(source_info)

        # Track report type
        if source_info['report_type'] not in self.merged_data['report_types']:
            self.merged_data['report_types'].append(source_info['report_type'])

        # Set title (use first non-empty)
        if not self.merged_data['title'] and report_data.get('title'):
            self.merged_data['title'] = report_data['title']

        # Merge period (use widest range)
        self._merge_period(report_data.get('period', {}), source_info)

        # Merge presence passive data
        self._merge_presence_passive(report_data.get('presence_passive', {}), source_info)

        # Merge presence active data
        self._merge_presence_active(report_data.get('presence_active', {}), source_info)

        # Merge volume data
        self._merge_volume(report_data.get('volume', {}), source_info)

        # Merge reach data
        self._merge_reach(report_data.get('reach', {}), source_info)

        # Merge sentiment data
        self._merge_sentiment(report_data.get('sentiment', {}), source_info)

        # Merge emotion data
        self._merge_emotion(report_data.get('emotion', {}), source_info)

        # Merge sources data
        self._merge_sources(report_data.get('sources', {}), source_info)

        # Merge languages data
        self._merge_languages(report_data.get('languages', {}), source_info)

        # Merge topics
        self._merge_topics(report_data.get('topics', []), source_info)

        # Merge hashtags
        self._merge_hashtags(report_data.get('hashtags', []), source_info)

        # Merge influencers
        self._merge_influencers(report_data.get('influencers', []), source_info)

        # Merge reach breakdown
        self._merge_reach_breakdown(report_data.get('reach_breakdown', []), source_info)

        # Merge demographics
        self._merge_demographics(report_data.get('demographics', {}), source_info)

    def _merge_period(self, period: Dict, source_info: Dict):
        """Merge period, taking the widest date range"""
        if period.get('start'):
            if not self.merged_data['period']['start'] or period['start'] < self.merged_data['period']['start']:
                self.merged_data['period']['start'] = period['start']
                self._track_source('period_start', period['start'], source_info)

        if period.get('end'):
            if not self.merged_data['period']['end'] or period['end'] > self.merged_data['period']['end']:
                self.merged_data['period']['end'] = period['end']
                self._track_source('period_end', period['end'], source_info)

    def _merge_presence_passive(self, data: Dict, source_info: Dict):
        """Merge presence passive data, preferring non-zero values"""
        for key in ['followers', 'followers_evolution', 'views', 'views_evolution',
                    'potential_reach', 'reach_evolution']:
            if data.get(key) and (not self.merged_data['presence_passive'].get(key) or
                                   self.merged_data['presence_passive'].get(key) == 0):
                self.merged_data['presence_passive'][key] = data[key]
                self._track_source(f'presence_passive.{key}', data[key], source_info)

    def _merge_presence_active(self, data: Dict, source_info: Dict):
        """Merge presence active data, preferring non-zero values"""
        for key in ['comments', 'likes', 'shares']:
            if data.get(key) and (not self.merged_data['presence_active'].get(key) or
                                   self.merged_data['presence_active'].get(key) == 0):
                self.merged_data['presence_active'][key] = data[key]
                self._track_source(f'presence_active.{key}', data[key], source_info)

    def _merge_volume(self, data: Dict, source_info: Dict):
        """Merge volume data"""
        if data.get('mentions') and not self.merged_data['volume'].get('mentions'):
            self.merged_data['volume']['mentions'] = data['mentions']
            self._track_source('volume.mentions', data['mentions'], source_info)
        if data.get('change_percent') and not self.merged_data['volume'].get('change_percent'):
            self.merged_data['volume']['change_percent'] = data['change_percent']
            self._track_source('volume.change_percent', data['change_percent'], source_info)

    def _merge_reach(self, data: Dict, source_info: Dict):
        """Merge reach data"""
        if data.get('reach') and not self.merged_data['reach'].get('reach'):
            self.merged_data['reach']['reach'] = data['reach']
            self._track_source('reach.reach', data['reach'], source_info)
        if data.get('change_percent') and not self.merged_data['reach'].get('change_percent'):
            self.merged_data['reach']['change_percent'] = data['change_percent']
            self._track_source('reach.change_percent', data['change_percent'], source_info)

    def _merge_sentiment(self, data: Dict, source_info: Dict):
        """Merge sentiment data - average percentages if multiple sources"""
        if not data:
            return

        for key in ['positive', 'negative', 'neutral']:
            if data.get(key) is not None:
                if key not in self.merged_data['sentiment']:
                    self.merged_data['sentiment'][key] = data[key]
                    self._track_source(f'sentiment.{key}', data[key], source_info)
                # If we have multiple sources, we keep the first (could average if needed)

    def _merge_emotion(self, data: Dict, source_info: Dict):
        """Merge emotion data"""
        if not data:
            return

        for key in ['admiration', 'anger', 'disgust', 'fear', 'joy', 'sadness', 'neutral']:
            if data.get(key) is not None:
                if key not in self.merged_data['emotion']:
                    self.merged_data['emotion'][key] = data[key]
                    self._track_source(f'emotion.{key}', data[key], source_info)

    def _merge_sources(self, data: Dict, source_info: Dict):
        """Merge sources data (platforms/sites)"""
        if not data:
            return

        for source_name, count in data.items():
            if source_name not in self.merged_data['sources']:
                self.merged_data['sources'][source_name] = count
                self._track_source(f'sources.{source_name}', count, source_info)
            else:
                # Add to existing count
                self.merged_data['sources'][source_name] += count

    def _merge_languages(self, data: Dict, source_info: Dict):
        """Merge languages data"""
        if not data:
            return

        for lang, count in data.items():
            if lang not in self.merged_data['languages']:
                self.merged_data['languages'][lang] = count
                self._track_source(f'languages.{lang}', count, source_info)
            else:
                self.merged_data['languages'][lang] += count

    def _merge_topics(self, topics: List, source_info: Dict):
        """Merge topics, combining counts for duplicate topics"""
        if not topics:
            return

        existing_topics = {t.get('name', t.get('topic', '')): t for t in self.merged_data['topics']}

        for topic in topics:
            name = topic.get('name', topic.get('topic', ''))
            if not name:
                continue

            if name in existing_topics:
                # Add counts
                existing_topics[name]['count'] = existing_topics[name].get('count', 0) + topic.get('count', 0)
            else:
                new_topic = {'name': name, 'count': topic.get('count', 0)}
                self.merged_data['topics'].append(new_topic)
                existing_topics[name] = new_topic
                self._track_source(f'topics.{name}', topic.get('count', 0), source_info)

    def _merge_hashtags(self, hashtags: List, source_info: Dict):
        """Merge hashtags, combining counts for duplicates"""
        if not hashtags:
            return

        existing_hashtags = {}
        for h in self.merged_data['hashtags']:
            tag = h.get('hashtag', h.get('name', ''))
            if tag:
                existing_hashtags[tag.lower()] = h

        for hashtag in hashtags:
            tag = hashtag.get('hashtag', hashtag.get('name', ''))
            if not tag:
                continue

            tag_lower = tag.lower()
            if tag_lower in existing_hashtags:
                existing_hashtags[tag_lower]['count'] = existing_hashtags[tag_lower].get('count', 0) + hashtag.get('count', 0)
            else:
                new_hashtag = {'hashtag': tag, 'count': hashtag.get('count', 0)}
                self.merged_data['hashtags'].append(new_hashtag)
                existing_hashtags[tag_lower] = new_hashtag
                self._track_source(f'hashtags.{tag}', hashtag.get('count', 0), source_info)

    def _merge_influencers(self, influencers: List, source_info: Dict):
        """Merge influencers, avoiding duplicates"""
        if not influencers:
            return

        existing_names = {inf.get('name', '').lower() for inf in self.merged_data['influencers']}

        for influencer in influencers:
            name = influencer.get('name', '')
            if not name or name.lower() in existing_names:
                continue

            self.merged_data['influencers'].append(influencer.copy())
            existing_names.add(name.lower())
            self._track_source(f'influencers.{name}', influencer.get('score', 0), source_info)

    def _merge_reach_breakdown(self, reach_data: List, source_info: Dict):
        """Merge reach breakdown data"""
        if not reach_data:
            return

        # For reach breakdown, just append all items with source tracking
        for item in reach_data:
            item_copy = item.copy()
            item_copy['source'] = source_info['filename']
            self.merged_data['reach_breakdown'].append(item_copy)
            self._track_source('reach_breakdown', item.get('reach', 0), source_info)

    def _merge_demographics(self, data: Dict, source_info: Dict):
        """Merge demographics data"""
        if not data:
            return

        for key in ['gender', 'age', 'countries', 'occupation', 'education', 'interests']:
            if data.get(key) and not self.merged_data['demographics'].get(key):
                self.merged_data['demographics'][key] = data[key]
                self._track_source(f'demographics.{key}', 'present', source_info)

    def _track_source(self, field: str, value: Any, source_info: Dict):
        """Track which report provided which data"""
        self.data_sources[field].append({
            'report_id': source_info['report_id'],
            'filename': source_info['filename'],
            'report_type': source_info['report_type'],
            'value': value
        })

    def _finalize_merged_data(self):
        """Sort and finalize merged data"""
        # Sort topics by count
        self.merged_data['topics'] = sorted(
            self.merged_data['topics'],
            key=lambda x: x.get('count', 0),
            reverse=True
        )

        # Sort hashtags by count
        self.merged_data['hashtags'] = sorted(
            self.merged_data['hashtags'],
            key=lambda x: x.get('count', 0),
            reverse=True
        )

        # Sort influencers by score
        self.merged_data['influencers'] = sorted(
            self.merged_data['influencers'],
            key=lambda x: x.get('score', 0),
            reverse=True
        )

        # Sort sources by count
        if self.merged_data['sources']:
            self.merged_data['sources'] = dict(sorted(
                self.merged_data['sources'].items(),
                key=lambda x: x[1],
                reverse=True
            ))

        # Sort languages by count
        if self.merged_data['languages']:
            self.merged_data['languages'] = dict(sorted(
                self.merged_data['languages'].items(),
                key=lambda x: x[1],
                reverse=True
            ))


def merge_multiple_reports(reports_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convenience function to merge multiple reports.

    Args:
        reports_data: List of extracted data dictionaries from each report

    Returns:
        Merged data dictionary with source tracking
    """
    merger = DataMerger()
    return merger.merge_reports(reports_data)
