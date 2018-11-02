from qiita_v2.client import QiitaClient

from datetime import datetime as dt

import os


class ReservationPostQiita(object):

  def __init__(self, access_token):
    self.access_token = access_token
    self.resrvation_items = []
    self.client = QiitaClient(access_token=os.environ['QIITA_ACCESS_TOKEN'])
    self._get_all_items()
    print(f'all_items: {len(self.items)}')

  def _get_all_items(self):
    self.items = []
    params = {
      'page': 1,
      'per_page': 100
    }
    while True:
      items = self.client.get_authenticated_user_items(params=params)
      self.items.extend(items.to_json())
      params['page'] += 1
      if 'next' not in items.links:
        break


  def get_reservation_items(self, post_datetime):

    # 限定共有投稿に絞り込む
    private_items = list(filter(lambda x: x['private'] == True, self.items))
    print(f'private items: {len(private_items)}')

    # 投稿日時の指定コメントされている投稿に絞り込む
    comments_items = list(filter(lambda x: x['comments_count'] > 0, private_items))
    print(f'commented items: {len(comments_items)}')

    # 記事コメントに予約投稿キーワードが含まれる記事に絞り込む
    self.resrvation_items = []
    for item in comments_items:
      comments = self.client.list_item_comments(item['id']).to_json()
      keyword = f'予約投稿:{post_datetime}'
      resrvation_comments = list(filter(lambda x: keyword in x['body'], comments))
      if len(resrvation_comments) > 0:
        self.resrvation_items.append(item)

    print(f'resrvation items: {len(self.resrvation_items)}')


  def post_items(self):
    for item in self.resrvation_items:
      # 記事を投稿する
      postParams = {}
      for key in ['title', 'body', 'tags']:
        postParams[key] = item[key]
      postParams['title'] = '【自動投稿】' + postParams['title']
      postParams['private'] = True # Test
      post_res = self.client.create_item(postParams)
      print(post_res.status)
      print('posted: ' + item['title'])

      # 限定共有投稿を削除する
      del_res = self.client.delete_item(item['id'])
      print(del_res.status)
      print('deleted: '  + item['title'])

      # TODO: twitterに投稿する


if __name__ == '__main__':
  client = ReservationPostQiita('')

  # 予約投稿を取得する
  datetime = dt.now().strftime('%Y/%m/%d %H:00')
  client.get_reservation_items(datetime)

  # 記事を投稿する
  client.post_items()

  # TODO: slackに通知する
