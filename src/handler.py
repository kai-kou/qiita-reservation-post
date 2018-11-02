import json

from src.main import *


def main(event, context):
  access_token = os.environ['QIITA_ACCESS_TOKEN']
  client = ReservationPostQiitaClient(access_token)

  # 予約投稿を取得する
  reservation_keyword = dt.now().strftime(os.environ['RESERVATION_KEYWORD'])
  print(f'reservation_keyword: {reservation_keyword}')
  client.get_reservation_items(reservation_keyword)

  # 記事を投稿する
  client.post_items()

  # TODO: slackに通知する
