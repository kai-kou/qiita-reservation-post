import json

from src.main import *


def main(event, context):
  access_token = os.getenv('QIITA_ACCESS_TOKEN', '')
  slack_web_hook_url = os.getenv('SLACK_WEB_HOOK_URL', None)
  keyword_format = os.getenv('RESERVATION_KEYWORD', '予約投稿:%Y/%m/%d %H:00')

  client = ReservationPostQiitaClient(access_token, slack_web_hook_url=slack_web_hook_url)

  # 予約投稿を取得する
  reservation_keyword = dt.now().strftime(keyword_format)
  print(f'reservation_keyword: {reservation_keyword}')
  client.get_reservation_items(reservation_keyword)

  # 記事を投稿する
  client.post_items()
