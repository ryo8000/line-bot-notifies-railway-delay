# 開発者向け情報

---

## 環境構築手順（初回）

※VSCode を使用します。

1. VSCode の拡張機能「Remote - Containers」をインストールし、リモートコンテナでワークスペースを開く。

2. 以下のコマンドを実行する。

```bash
# Lambdaレイヤーを用意
pip3 install -r requirements.txt -t ./layers/line-bot-sdk/python
# Serverless Frameworkのプラグインを用意
cd app/
npm install
```

3. 以下のファイルに必要な情報を記載する。

- config/serverless.yml {deploymentBucket}: S3 デプロイ先

4. 以下のコマンドを実行する。

```bash
sls config credentials --provider aws --key {AWSアクセスキー} --secret {AWSシークレットキー}
```

5. デプロイする。デプロイ手順は以降に記載。

6. LINE Developers のアカウントを作成する。

7. 新規チャネルを作成する。チャネルの種類は Messaging API。

8. 作成したチャネルの Webhook URL に、デプロイした API Gateway の URL を貼り付ける。

9. 作成したチャネルの応答メッセージを無効にする。

10. 作成したチャネルのチャネルアクセストークンとチャネルシークレットを発行する。

11. 以下のファイルに必要な情報を記載する。

- config/dev.yml {LINE_CHANNEL_ACCESS_TOKEN}: 開発用チャネルアクセストークン
- config/dev.yml {LINE_CHANNEL_SECRET}: 開発用チャネルシークレット
- config/prod.yml {LINE_CHANNEL_ACCESS_TOKEN}: 本番用チャネルアクセストークン
- config/prod.yml {LINE_CHANNEL_SECRET}: 本番用チャネルシークレット

## 環境構築手順（二回目以降）

1. リモートコンテナでワークスペースを開く。

2. 以下のコマンドを実行する。

```bash
sls config credentials --provider aws --key {AWSアクセスキー} --secret {AWSシークレットキー}
```

## デプロイ手順

1. 以下のいずれかのコマンドを実行する。

```bash
cd app/
# 開発環境デプロイ
npm run deploy-dev
```

```bash
cd app/
# 本番環境デプロイ
npm run deploy-prod
```

## 構成について

### ディレクトリ構成

- app/: AWS 上にデプロイするファイル一式と Serverless Framework 用 モジュール。
- config/: デプロイ用ファイル一式。
- layers/: Lambda レイヤー用。

### AWS 構成

- Lambda 関数: 通知用と応答用の 2 つ。
- Lambda レイヤー: line-bot-sdk などのサードパーティ製ライブラリを格納します。
- API Gateway: 応答用 Lambda 用。LINE Bot の Webhook URL になります。
- EventBridge: 通知用 Lambda 用。通知時間を設定します。
- IAM: Lambda 用のロール。
- CloudWatch: Lambda 用のログ。
- DynamoDB: ユーザ情報用テーブルが 1 つ。
- CloudFormation: 上記のサービス一式がまとまったスタックが 1 つ。

### 通知処理について

- 所定の時間帯に遅延情報を確認し、遅延があれば全ユーザに通知します。
- 遅延情報がない、もしくは前回通知した遅延情報から変化がない場合は通知しません。

### 応答処理について

- 送信されたメッセージ内容に応じて遅延情報を返答します。それ以外の機能はおまけです。
- 鉄道遅延情報の取得先に過度なリクエストを送信しないよう、一定時間内に遅延情報を確認する場合は、DynamoDB に登録されてある遅延情報を使用するようにしています。
- DynamoDB のユーザ情報用テーブルには、サービスを利用しているユーザのデータ（ID は LINE ユーザ ID）と、遅延情報用のデータ（ID は"railway"）が混在しています。本来テーブルを分けるべきですが、使用料金を抑えるために同一のテーブルを使用しています。

### 友達削除について

- ブロックやフォロー解除を行ったユーザの情報は、ユーザ情報用テーブルから削除します。
