import os
import random
from itertools import chain
from textwrap import dedent

import httplib2
from dotenv import load_dotenv
from flask import request

load_dotenv()

import openai
from googleapiclient.discovery import build
from joblib import Parallel, delayed

cities = [
    "鹿児島",
    "鹿屋",
    "枕崎",
    "阿久根市",
    "出水市",
    "指宿",
    "西之表",
    "垂水市",
    "薩摩川内",
    "日置市",
    "曽於市",
    "霧島市",
    "いちき串木野",
    "南さつま",
    "志布志",
    "奄美",
    "南九州市",
    "伊佐市",
    "姶良",
]


def collect_google_info(query: str, additional_key="鹿児島") -> list[dict[str, str]]:
    # Google Custom Search API を使って検索

    service = build(
        "customsearch", "v1", developerKey=os.environ["GOOGLE_API_KEY"]
    ).cse()

    data = []

    # http = google_auth_httplib2.AuthorizedHttp(credentials, http=httplib2.Http())
    res = service.list(
        q=additional_key + " " + query, cx=os.environ["GOOGLE_CSE_ID"]
    ).execute(http=httplib2.Http())

    if "items" not in res:
        return []

    for obj in res["items"]:
        desc = obj["snippet"]

        if "pagemap" in obj and obj["pagemap"].get("metatags", []):
            target = obj["pagemap"]["metatags"][0]
            if "og:description" in target:
                desc += "\n" + target["og:description"]
            elif "twitter:description" in target:
                desc += "\n" + target["twitter:description"]

        data.append({"title": obj["title"], "link": obj["link"], "desc": desc})

    return data


def search_web(query: str) -> list[dict[str, str]]:
    if any(city in query for city in cities):
        return collect_google_info(query, "")
    else:
        result = Parallel(n_jobs=2)(
            [
                delayed(collect_google_info)(query, city)
                for city in (random.choices(cities[1:], k=3) + ["鹿児島"])
            ]
        )
        flattened = list(chain.from_iterable([r[:7] if r else [] for r in result]))
        return flattened
        # return random.choices(flattened, k=20)


def propose_query(messages: list):
    instruction = """\
    最後のユーザのコメントに適切に応答するための情報収集としてweb検索をします。
    そのための適切な検索キーワードを出力してください。
    ルール：
    - 回答はスペース区切りでキーワードのみ答えてください
    - キーワードがない場合は""を返してください
    
    Q: 今年のWBCのMVPは誰ですか？ 
    A: "WBC 2023 MVP"
    Q: はアむAけごす
    A: ""
    Q: 初代ポケットモンスターのゲームに登場するポケモンは何種類か知りたい
    A: "初代 ポケモン 種類"
    Q: なんか暇だなあ
    A: "暇つぶし 方法"
    Q: 人生に疲れた
    A: "癒し スポット"
    """
    additional = {"role": "system", "content": dedent(instruction)}
    tmp_messages = [
        m for idx, m in enumerate(messages) if idx == 0 or m["role"] != "system"
    ] + [additional]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=tmp_messages,
        timeout=60,
    )
    return response["choices"][0]["message"]["content"].strip('"')


def get_remote_address():
    if "X-Forwarded-For" in request.headers:
        # X-Forwarded-For header can be a comma-separated list of IPs.
        # The client's requested IP is the first one.
        return request.headers["X-Forwarded-For"].split(",")[0]
    else:
        return request.remote_addr
