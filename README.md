# Translation App

これはFlaskとOpenAI APIを利用した簡単な日英翻訳アプリケーションです。

## 機能

- 日本語を英語に翻訳します。
- 翻訳結果を単語に分割し、意味と発音を表示します。
- 気に入った単語を単語帳に保存できます。

## セットアップ方法

1.  リポジトリをクローンします。
    ```bash
    git clone https://github.com/YOUR_USERNAME/translation_app.git
    cd translation_app
    ```

2.  必要なパッケージをインストールします。
    ```bash
    pip install -r requirements.txt
    ```

3.  `.env`ファイルを作成し、APIキーを設定します。
    ```
    OPENAI_API_KEY="your_openai_api_key"
    APP_SECRET_KEY="your_secret_key"
    ```

4.  アプリケーションを実行します。
    ```bash
    flask run
    ```
