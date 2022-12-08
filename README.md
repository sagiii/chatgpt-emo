# 概要
ChatGPTにユカイ工学の[BOCCO emo](https://www.bocco.me/)をつなぐサンプルコードです。

# 必要なもの
- BOCCO emo
- ChatGPTのアカウント

# セットアップ
コマンドの実行が必要そうなので、requirementsではなくスクリプトにしてみました：
```
./install.sh
```

ChatGPTのセットアップ時にブラウザが起動してChatGPTのアカウントでログインなどが必要になります。
一回ログインすると次回からログインは不要になります。

# 使い方
1. [BOCCO emo Platform APIドキュメント](https://platform-api.bocco.me/api-docs/#overview--bocco-emo-platform-api%E3%81%A8%E3%81%AF)に従い、アクセストークンとリフレッシュトークンを取得してください。
1. run.shのexportに、アクセストークンとリフレッシュトークンを記入してください。
1. run.shのexportに、ChatGPTにつなぎたいBOCCO emoのルームの名前を記入してください。
1. `./run.sh` で実行してください。
