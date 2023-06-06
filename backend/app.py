import os
import re
import uuid
from datetime import timedelta
from textwrap import dedent

import redis
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request, session, stream_with_context
from flask_cors import CORS
from flask_limiter import Limiter

# from flask_limiter.util import get_remote_address
from flask_session import Session

from util import get_remote_address, propose_query, search_web

load_dotenv()

import openai

app = Flask(__name__)

app.config["JSON_AS_ASCII"] = False
# app.config["JWT_SECRET_KEY"] = "super-secret"
# app.config['JWT_ALGORITHM'] = 'HS256'                       # 暗号化署名のアルゴリズム
# app.config['JWT_LEEWAY'] = 0                                # 有効期限に対する余裕時間
# app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=300) # トークンの有効期間
# app.config['JWT_NOT_BEFORE_DELTA'] = timedelta(seconds=0)   # トークンの使用を開始する相対時間
# app.config['JWT_AUTH_URL_RULE'] = '/auth'                   # 認証エンドポイントURL

# jwt = JWTManager(app)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

app.config.update(
    DEBUG=True,
    SECRET_KEY="super-secret",
    # SESSION_COOKIE_HTTPONLY=True,
    # REMEMBER_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE=None,
    SESSION_REFRESH_EACH_REQUEST=False,
)
app.permanent_session_lifetime = timedelta(minutes=10)

# Configure Redis for storing the session data on the server-side
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
# app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
app.config["SESSION_REDIS"] = redis.Redis(
    "localhost" if os.environ.get("FLASK_ENV", "local") == "local" else "redis"
)


# Create and initialize the Flask-Session object AFTER `app` has been configured
server_session = Session(app)


app.config["RATELIMIT_HEADERS_ENABLED"] = True
limiter = Limiter(get_remote_address, app=app, default_limits=["100/hour"])

init_mes = {
    "role": "system",
    "content": """\
あなたは鹿児島案内AIで、名前は「segoai」です。
今からの会話では、全ての返答において、鹿児島の魅力に具体例を挙げて言及してください。
""",
}


@app.before_request
def make_session_permanent():
    # refs: https://mulgrew.me/posts/session-timeout-flask.html
    session.permanent = True
    # app.permanent_session_lifetime = timedelta(minutes=10)
    session.modified = True


@app.route("/api/info", methods=["GET", "POST"])
def info():
    if "id" not in session:
        session["id"] = uuid.uuid4()
        session["messages"] = [init_mes]
    return jsonify(dict(session)), 200


def process_stream_data(stream, google_info: list[dict[str, str]]):
    # ストリームチャンクのレスポンスデータを加工するジェネレータ関数
    message = ""

    try:
        for chunk in stream:
            # データの加工処理を行う（例: 大文字に変換する）
            processed_chunk = chunk["choices"][0]["delta"].get("content", "")
            # print(processed_chunk, flush=True)
            message += processed_chunk
            yield processed_chunk

        if google_info:
            matches = re.findall(r"\(\s*\d+(?:\s*,\s*\d+)*\s*\)", message)
            m2 = [m[1:-1].split(",") for m in matches]
            indexes = sorted(list(set([int(_) - 1 for _ in sum(m2, [])])))
            yield "<br/>"
            for i in indexes:
                info = google_info[i]
                yield f"{i + 1}. <a href=\"{info['link']}\" target=\"_brank\">{info['title']}</a><br/>"
    finally:
        session["messages"].append({"role": "assistant", "content": message})


@app.route("/api/refresh", methods=["POST"])
def refresh():
    if "id" not in session:
        session["id"] = uuid.uuid4()
    session["messages"] = [init_mes]
    return jsonify(success=True), 201


@app.route("/api/chat", methods=["POST"])
# @limiter.limit("50/day")
def chat():
    if "id" not in session:
        session["id"] = uuid.uuid4()
        session["messages"] = [init_mes]
        return "セッションが切れているようです。ページをリロードします", 401

    user_message = request.get_data(as_text=True)
    print(user_message)

    session["messages"].append({"role": "user", "content": user_message})

    query = propose_query(session["messages"]) or user_message

    print(f"query: {query}")
    # google_info = collect_google_info(query)
    google_info = search_web(query)

    tmp_messages = session["messages"]

    if google_info:
        add_info = """\
        以下に参考データを並べます。回答に使用したdocの番号を、文末に記載してください
        例："天文館商店街には薩摩蒸気屋という老舗の菓子屋があります(1)。"
        例："鹿児島は晴天率が比較的高い地域です(2,3)。"
        """
        add_info = dedent(add_info) + "\n".join(
            [
                f"doc:{no}\n{g['title']}\n{g['desc']}"
                for no, g in enumerate(google_info, start=1)
            ]
        )
        additional_system_message = {"role": "system", "content": add_info}

        tmp_messages = (
            session["messages"][:-1]
            + [additional_system_message]
            + [session["messages"][-1]]
        )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=tmp_messages,
            timeout=60,
            stream=True,
        )
        return Response(
            stream_with_context(process_stream_data(response, google_info)),
            content_type="text/event-stream",
        )
    except openai.error.RateLimitError as e:
        print(str(e))
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=tmp_messages,
            timeout=60,
            stream=True,
        )
        return Response(
            stream_with_context(process_stream_data(response, google_info)),
            content_type="text/event-stream",
        )


@app.errorhandler(429)
def ratelimit_handler(e):
    return "申し訳ありません！LLM-API利用料金高騰を防ぐため、メッセージ回数を50回／日に制限しています", 429


@app.route("/api/myip", methods=["GET"])
def get_my_ip():
    return jsonify({"ip": get_remote_address()}), 200


if __name__ == "__main__":
    app.run()
