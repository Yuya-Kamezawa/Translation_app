import os
from typing import Any, Dict, List

import markdown
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI

# Flaskとデータベースの初期化
app: Flask = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///words.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db: SQLAlchemy = SQLAlchemy(app)

# 環境変数を読み込み、APIキーとセッションのシークレットキーを設定
load_dotenv()
client: OpenAI = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app.secret_key = os.getenv("APP_SECRET_KEY")


# 単語モデルの作成
class Word(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    english: str = db.Column(db.String(100), nullable=False)
    japanese: str = db.Column(db.String(100), nullable=False)
    pronunciation: str = db.Column(db.String(100), nullable=False)


# データベースの初期化
with app.app_context():
    db.create_all()


# セッションを初期化するための関数
def initialize_session():
    session.clear()
    session["messages"] = [
        # 役割の設定
        {
            "role": "system",
            "content": "あなたは、子供向けにシンプルにわかりやすく教える英語の先生です。日常会話で使えるフランクな英語を教えてください。",
        }
    ]


# セッションに会話を追加するための関数
def append_session(role: str, content: str):
    messages: List = session["messages"]
    messages.append({"role": role, "content": content})
    session["messages"] = messages


# ChatGPTと会話するための関数
def ask_chatgpt(user_question: str, model: str = "gpt-4o-mini", raw_text: bool = False):
    # ユーザーの質問をセッションに追加
    append_session("user", user_question)

    # ChatGPTのAPIを使って、質問する
    response: Dict[str, Any] = client.chat.completions.create(
        model=model,
        messages=session["messages"],
    )

    # ChatGPTの回答を取得し、セッションに追加
    chatgpt_answer: str = response.choices[0].message.content
    append_session("assistant", chatgpt_answer)

    if raw_text:
        return chatgpt_answer
    else:
        # ChatGPTの回答をhtml文字列に変換して返却
        return markdown.markdown(chatgpt_answer)


# 「/」にアクセスがあった場合のルーティング
@app.route("/")
def index():
    return render_template("index.html")


# 「/translate」にアクセスがあった場合のルーティング
@app.route("/translate", methods=["POST"])
def translate():
    # セッションを初期化
    initialize_session()

    # ユーザーの入力値を取得して、質問を作成
    user_input: str = request.form.get("user_input")
    user_question: str = "「" + user_input + "」" + "を英語に翻訳してください。"

    # ChatGPTに質問して、結果を取得
    translation_result: str = ask_chatgpt(user_question)

    # 結果を返却
    return render_template(
        "translation_result.html", translation_result=translation_result
    )


# 「/tokenize」にアクセスがあった場合のルーティング
@app.route("/tokenize", methods=["POST"])
def tokenize():
    # 質問を作成
    user_question: str = (
        "直前の翻訳結果を単語分割してください。以下のルールに厳密に従ってください:\n"
        "1. 1行に1単語ずつ出力する。\n"
        "2. 各行は「英単語|日本語の意味|発音記号」の形式にする。\n"
        "3. この形式以外の余計なテキスト（例えば「はい、承知しました」などの返事や説明）は一切含めないでください。"
    )
    # ChatGPTに質問して、結果を「生テキスト」で取得
    tokenization_result_raw: str = ask_chatgpt(user_question, raw_text=True)

    # 結果を解析して、リストに格納する
    tokenized_list = []
    for line in tokenization_result_raw.strip().split('\n'):
        parts = line.strip().split('|')
        if len(parts) == 3:
            tokenized_list.append({
                "english": parts[0].strip(),
                "japanese": parts[1].strip(),
                "pronunciation": parts[2].strip(),
            })

    # 結果を返却
    return render_template("tokenization_result.html", tokenized_list=tokenized_list)


# 「/word_list」にアクセスがあった場合のルーティング
@app.route("/word_list")
def word_list():
    words = Word.query.all()
    return render_template("word_list.html", words=words)


# 「/add_word」にアクセスがあった場合のルーティング
@app.route("/add_word", methods=["POST"])
def add_word():
    english = request.form["english"]
    japanese = request.form["japanese"]
    pronunciation = request.form["pronunciation"]
    word = Word(
        english=english,
        japanese=japanese,
        pronunciation=pronunciation,
    )
    db.session.add(word)
    db.session.commit()
    return redirect(url_for("word_list"))


# 「/delete_word」にアクセスがあった場合のルーティング
@app.route("/delete_word/<int:id>")
def delete_word(id):
    word = Word.query.get(id)
    db.session.delete(word)
    db.session.commit()
    return redirect(url_for("word_list"))


if __name__ == "__main__":
    app.run(debug=True)
