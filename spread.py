import argparse
import datetime
import gspread
import memcache
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials


class CredentialsWithMemcache(object):
    CACHE_KEY = 'goauth2:credentials'

    def __init__(self, key_json, force_refresh=False):
        self.scopes = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        self.key_json = key_json
        self._credentials = None
        self.mem_client = memcache.Client(['localhost:11211'])
        self.force_refresh = force_refresh

    @property
    def credentials(self):
        if self._credentials is None:
            if not self.force_refresh:
                self._credentials = self.from_config()
            if self._credentials is None:
                self._credentials = self.from_flow()
        return self._credentials

    def from_config(self):
        config = self.get_config()
        if not config:
            return
        return Credentials(
            config['access_token'],
            refresh_token=config['refresh_token'],
            token_uri=config['token_uri'],
            client_id=config['client_id'],
            client_secret=config['client_secret']
        )

    def from_flow(self):
        flow = InstalledAppFlow.from_client_secrets_file(self.key_json, self.scopes)
        credentials = flow.run_console()
        self.set_config(credentials)
        return credentials

    def get_config(self):
        return self.mem_client.get(self.CACHE_KEY)

    def set_config(self, credentials):
        expire = int((credentials.expiry - datetime.datetime.now()).total_seconds())
        self.mem_client.set(self.CACHE_KEY, {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
        }, expire)


class Gspread(object):
    def __init__(self, credentials):
        # oauth2clientはdeprecationなので使わないように
        # https://github.com/burnash/gspread/issues/472#issuecomment-317631725
        self.client = gspread.Client(auth=credentials)
        self.client.session = AuthorizedSession(credentials)


parser = argparse.ArgumentParser()
parser.add_argument('--key-json', help='credentials key json', required=True)
parser.add_argument('--force-refresh', action='store_true', help='force refresh token')

args = parser.parse_args()

spread = Gspread(
    CredentialsWithMemcache(args.key_json, args.force_refresh).credentials
)
print(spread.client.openall())
