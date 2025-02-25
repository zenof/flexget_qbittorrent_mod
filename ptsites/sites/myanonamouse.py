import re
from dateutil.parser import parse

from ..schema.site_base import SiteBase, Work, SignState, NetworkState

# site_config
#  login:
#    username: 'xxxxxxxx'
#    password: 'xxxxxxxx'

class MainClass(SiteBase):
    URL = 'https://www.myanonamouse.net/'
    USER_CLASSES = {
        'uploaded': [26843545600],
        'share_ratio': [2.0],
        'days': [28]
    }

    def build_workflow(self, entry, config):
        return [
            Work(
                url='/login.php',
                method='get',
                check_state=('network', NetworkState.SUCCEED),
            ),
            Work(
                url='/takelogin.php',
                method='login',
                succeed_regex='Log Out',
                response_urls=['/u/'],
                check_state=('final', SignState.SUCCEED),
                is_base_content=True,
                t_regex='<input type="hidden" name="t" value="([^"]+)"',
                a_regex='<input type="hidden" name="a" value="([^"]+)"',
            )
        ]

    def sign_in_by_login(self, entry, config, work, last_content):
        login = entry['site_config'].get('login')
        if not login:
            entry.fail_with_prefix('Login data not found!')
            return
        t = re.search(work.t_regex, last_content).group(1)
        a = re.search(work.a_regex, last_content).group(1)
        data = {
            't': t,
            'a': a,
            'email': login['username'],
            'password': login['password'],
            'rememberMe': 'yes'
        }
        return self._request(entry, 'post', work.url, data=data)

    def get_message(self, entry, config):
        self.get_myanonamouse_message(entry, config)

    def get_details(self, entry, config):
        self.get_details_base(entry, config, self.build_selector())

    def build_selector(self):
        return {
            'user_id': '/u/(\\d+)',
            'detail_sources': {
                'default': {
                    'link': '/u/{}',
                    'elements': {
                        'bar': '.mmUserStats ul',
                        'table': 'table.coltable'
                    }
                }
            },
            'details': {
                'uploaded': {
                    'regex': 'Uploaded.+?([\\d.]+ [ZEPTGMK]?B)'
                },
                'downloaded': {
                    'regex': 'Downloaded.+?([\\d.]+ [ZEPTGMK]?B)'
                },
                'share_ratio': {
                    'regex': 'Share ratio.*?(∞|[\\d,.]+)',
                    'handle': self.handle_share_ratio
                },
                'points': {
                    'regex': 'Bonus:\s+([\\d,.]+)'
                },
                'join_date': {
                    'regex': 'Join date\\s*?(\\d{4}-\\d{2}-\\d{2})',
                    'handle': self.handle_join_date
                },
                'seeding': None,
                'leeching': None,
                'hr': None
            }
        }

    def get_myanonamouse_message(self, entry, config, messages_url='/messages.php?action=viewmailbox'):
        entry['result'] += '(TODO: Message)'

    def handle_share_ratio(self, value):
        if value in ['---', '∞']:
            return '0'
        else:
            return value

    def handle_join_date(self, value):
        return parse(value).date()
