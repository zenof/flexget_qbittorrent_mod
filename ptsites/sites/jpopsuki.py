import datetime
import re

from ..schema.gazelle import Gazelle
from ..schema.site_base import Work, SignState


class MainClass(Gazelle):
    URL = 'https://jpopsuki.eu/'
    USER_CLASSES = {
        'uploaded': [26843545600],
        'share_ratio': [1.05],
        'days': [14]
    }

    def build_workflow(self, entry, config):
        return [
            Work(
                url='/',
                method='get',
                succeed_regex='JPopsuki 2.0',
                check_state=('final', SignState.SUCCEED),
                is_base_content=True
            )
        ]

    def build_selector(self):
        selector = {
            'user_id': 'user.php\\?id=(\\d+)',
            'detail_sources': {
                'default': {
                    'link': '/user.php?id={}',
                    'elements': {
                        'table': '#content > div > div.sidebar > div:nth-last-child(4) > ul',
                        'Community': '#content > div > div.sidebar > div:last-child > ul'

                    }
                }
            },
            'details': {
                'uploaded': {
                    'regex': 'Uploaded: ([\\d.]+ ?[ZEPTGMK]?B)'
                },
                'downloaded': {
                    'regex': 'Downloaded: ([\\d.]+ ?[ZEPTGMK]?B)'
                },
                'share_ratio': {
                    'regex': 'Ratio: (--|∞|[\\d,.]+)',
                    'handle': self.handle_share_ratio
                },
                'points': {
                    'regex': 'Bonus Points: ([\\d,.]+)',
                },
                'join_date': {
                    'regex': 'Joined: (.*?ago)',
                    'handle': self.handle_join_date
                },
                'seeding': {
                    'regex': 'Seeding: ([\\d,]+)'
                },
                'leeching': {
                    'regex': 'Leeching: ([\\d,]+)'
                },
                'hr': None
            }
        }
        return selector

    def handle_share_ratio(self, value):
        if value in ['--', '∞']:
            return '0'
        else:
            return value

    def handle_join_date(self, value):
        year_regex = '(\\d+) years?'
        month_regex = '(\\d+) months?'
        week_regex = '(\\d+) weeks?'
        year = 0
        month = 0
        week = 0
        if year_match := re.search(year_regex, value):
            year = int(year_match.group(1))
        if month_match := re.search(month_regex, value):
            month = int(month_match.group(1))
        if week_match := re.search(week_regex, value):
            week = int(week_match.group(1))
        return (datetime.datetime.now() - datetime.timedelta(days=year * 365 + month * 31 + week * 7)).date()
