import json

from src.main import *


def main(event, context):
  qiita_access_token = os.getenv('QIITA_ACCESS_TOKEN', '')
  slack_web_hook_url = os.getenv('SLACK_WEB_HOOK_URL', None)
  keyword_format = os.getenv('RESERVATION_KEYWORD', '予約投稿:%Y/%m/%d %H:00')
  twitter_api_key = os.getenv('TWITTER_API_KEY', None)
  twitter_api_secret_key = os.getenv('TWITTER_API_SECRET_KEY', None)
  twitter_access_token = os.getenv('TWITTER_ACCESS_TOKEN', None)
  twitter_access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', None)

  twitter_keys = None
  if twitter_api_key is not None:
    twitter_keys = {
      'twitter_api_key': twitter_api_key,
      'api_secret_key': twitter_api_secret_key,
      'access_token': twitter_access_token,
      'access_token_secret': twitter_access_token_secret
    }

  client = ReservationPostQiitaClient(
    qiita_access_token,
    slack_web_hook_url=slack_web_hook_url,
    twitter_keys=twitter_keys)

  # 予約投稿を取得する
  reservation_keyword = dt.now().strftime(keyword_format)
  print(f'reservation_keyword: {reservation_keyword}')
  client.get_reservation_items(reservation_keyword)

  # 記事を投稿する
  client.post_items()
