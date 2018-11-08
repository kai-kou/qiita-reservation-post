from qiita_v2.client import QiitaClient

from datetime import datetime as dt

import os

import slackweb

import twitter


class ReservationPostQiitaClient(object):

  def __init__(self, access_token, slack_web_hook_url=None, twitter_keys=None):
    self.access_token = access_token
    self.resrvation_items = []
    self.client = QiitaClient(access_token=access_token)
    self._get_all_items()
    print(f'all_items: {len(self.items)}')

    self.slack = None
    if slack_web_hook_url is not None:
      self.slack = slackweb.Slack(url=slack_web_hook_url)

    self.twitter = None
    if twitter_keys is not None:
      tw_auth = twitter.OAuth(
                  consumer_key=twitter_keys['twitter_api_key'],
                  consumer_secret=twitter_keys['api_secret_key'],
                  token=twitter_keys['access_token'],
                  token_secret=twitter_keys['access_token_secret'])
      self.twitter = twitter.Twitter(auth=tw_auth)


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


  def get_reservation_items(self, reservation_keyword):

    self.resrvation_items = []

    # 限定共有投稿に絞り込む
    private_items = list(filter(lambda x: x['private'] == True, self.items))
    print(f'private items: {len(private_items)}')

    # 投稿日時の指定コメントされている投稿に絞り込む
    comments_items = list(filter(
      lambda x: x['comments_count'] > 0 and reservation_keyword not in x['title'], private_items))
    print(f'commented items: {len(comments_items)}')

    # 記事コメントに予約投稿キーワードが含まれる記事を取得する
    resrvation_comment_items = []
    for item in comments_items:
      comments = self.client.list_item_comments(item['id']).to_json()
      resrvation_comments = list(filter(lambda x: reservation_keyword in x['body'], comments))
      if len(resrvation_comments) > 0:
        resrvation_comment_items.append(item)
    print(f'resrvation comment items: {len(resrvation_comment_items)}')

    # タイトルに予約投稿キーワードが含まれる記事を取得する
    resrvation_title_items = []
    title_items = list(filter(lambda x: reservation_keyword in x['title'], private_items))

    # タイトルから予約投稿キーワードを除外しておく
    for item in title_items:
      item['title'] = item['title'].replace(reservation_keyword, '')
    print(f'resrvation title items: {len(title_items)}')

    # コメント・タイトルそれぞれから取得した記事をまとめる
    self.resrvation_items.extend(resrvation_comment_items)
    self.resrvation_items.extend(title_items)
    print(f'resrvation items: {len(title_items)}')


  def post_items(self):
    for item in self.resrvation_items:
      # 記事を公開投稿する
      postParams = {}
      for key in ['title', 'body', 'tags']:
        postParams[key] = item[key]
      postParams['private'] = False
      post_res = self.client.create_item(postParams)

      if post_res.status != 201:
        print(f'error status: {post_res.status}')
        # エラーの場合はとりあえず落とす
        return
      new_item = post_res.to_json()
      print('posted: ' + new_item['title'])

      # 限定共有投稿を削除する
      del_res = self.client.delete_item(item['id'])
      if del_res.status != 204:
        print(f'error status: {post_res.status}')
      print('deleted: '  + item['title'])

      # twitterに投稿する
      self._twitter_statuses_update(f'''{new_item['title']} on @Qiita
{new_item['url']}
      ''')

      # slackに通知する
      self._slack_notify(f'''Qiitaに投稿しました
      {new_item['title']}
      {new_item['url']}
      ''')


  def _slack_notify(self, text):
    if self.slack is None:
      return
    self.slack.notify(text=text)
    print(f'slack.notify: {text}')


  def _twitter_statuses_update(self, status):
    if self.twitter is None:
        return
    self.twitter.statuses.update(status=status)
    print(f'twitter.statuses.update: {status}')
