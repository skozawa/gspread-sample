## Google Spreadsheet sample

- require
  - memcached

- setup
  - pyenv install
```
$ python -m venv venv
$ . venv/bin/activate
# pip -r requirements.txt
```
  - Generate Google OAuth2 Client ID
    - https://console.developers.google.com/
    - spreadsheetとgoogle driveを有効化
    - OAuthクライアントを作成
    - client_secret_....json をダウンロード
      - key-jsonで利用

- exec
```
$ python spread.py -h
usage: spread.py [-h] --key-json KEY_JSON [--force-refresh]

optional arguments:
  -h, --help           show this help message and exit
  --key-json KEY_JSON  credentials key json
  --force-refresh      force refresh token
```
