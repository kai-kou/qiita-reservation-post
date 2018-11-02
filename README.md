# qiita-reservation-post

Qiita予約投稿ツール  

## Deploy to AWS Lambda

```sh
> git clone https://github.com/kai-kou/qiita-reservation-post.git
> cd qiita-reservation-post
# Edit serverless.yaml functions.environment.QIITA_ACCESS_TOKEN
> vi serverless.yaml

> npm install -g serverless

# Setting AWS credentials
# > serverless config credentials --provider aws --key XXXXXXXXXXXXEXAMPLE --secret XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXEXAMPLE

> npm install
> serverless deploy
```
