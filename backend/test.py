import os
import random
import re
from textwrap import dedent

import httplib2
from dotenv import load_dotenv
from joblib import Parallel, delayed

load_dotenv()

from itertools import chain

import openai
from googleapiclient.discovery import build
from rich.console import Console

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
                for city in random.choices(cities, k=4)
            ]
        )
        flattened = list(chain.from_iterable(result))
        return random.choices(flattened, k=20)


def propose_query(messages: list):
    instruction = """\
    最後のユーザのコメントに適切に応答するための情報収集としてweb検索をします。
    そのための適切な検索キーワードを出力してください。
    ルール：
    - 回答はスペース区切りでキーワードのみ答えてください
    - キーワードがない場合は""を返してください
    
    Q: 今年のWBCのMVPは誰ですか？ 
    A: "WBC 2023 MVP"
    Q: 初代ポケットモンスターのゲームに登場するポケモンは何種類か知りたい
    A: "初代 ポケモン 種類"
    Q: Linuxで使えるコマンドとその意味を分かりやすくリストアップしてほしい
    A: "Linux コマンド 一覧 初心者"
    Q: なんか暇だなあ
    A: "暇つぶし 方法"
    Q: 人生に疲れた
    A: "癒し スポット"
    """
    additional = {"role": "system", "content": dedent(instruction)}
    tmp_messages = [
        m for idx, m in enumerate(messages) if idx == 0 or m["role"] != "system"
    ] + [additional]

    for m in tmp_messages:
        print(m)

    response = openai.ChatCompletion.create(
        model="gpt-4",
        # temperature = 0.0,
        messages=tmp_messages,
        timeout=60,
    )
    return response["choices"][0]["message"]["content"].strip('"')


chat_log = [
    {
        "role": "system",
        "content": """\
あなたは熱烈な鹿児島ファンです。
今からの会話では、全ての返答において、鹿児島の魅力に具体例を挙げて言及してください。
""",
    }
]

blue = "\033[34m"
green = "\033[32m"
red = "\033[31m"
bold = "\033[1m"
reset = "\033[0m"

console = Console()

while True:
    prompt = input(bold + blue + "Enter a prompt (or 'q'): " + reset + "\n")

    if prompt.lower() == "q":
        break

    chat_log.append({"role": "user", "content": prompt})

    query = propose_query(chat_log) or prompt

    print(f"query: {query}")
    google_info = search_web(query)
    additional_system_message = None
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
        print(add_info)
        additional_system_message = {"role": "system", "content": add_info}

    # 回答する際の注意事項：文中に対応する参考文献の番号を【文献1】のように出力してください

    response = openai.ChatCompletion.create(
        # model = "gpt-3.5-turbo",
        model="gpt-4",
        # temperature = 0.0,
        messages=(chat_log[:-1] + [additional_system_message] + [chat_log[-1]])
        if additional_system_message
        else chat_log,
        timeout=30,
        stream=True,
    )

    content = ""
    for chunk in response:
        next: str = chunk["choices"][0]["delta"].get("content", "")  # type: ignore
        # text += next
        # if "。" in next:
        #     text += "\n"
        content += next
        print(next, flush=True, end="")


    print(content)
    chat_log.append({"role": "assistant", "content": content})

    if google_info:
        matches = re.findall(r"\(\s*\d+(?:\s*,\s*\d+)*\s*\)", content)
        m2 = [m[1:-1].split(",") for m in matches]
        indexes = [int(_) - 1 for _ in sum(m2, [])]
        for i in indexes:
            print(google_info[i])

