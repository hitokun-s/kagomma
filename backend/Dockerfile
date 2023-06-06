FROM python:3.9-buster
#FROM nikolaik/python-nodejs:python3.9-nodejs16-slim

ENV TZ="Asia/Tokyo"

#RUN apk update && apk add build-base && apk add python3-dev gcc libc-dev

ENV HOST 0.0.0.0
ENV PORT 5000
ENV DEBUG true

COPY . /app
WORKDIR /app


#ARG work_dir="/work/"
##ARG project_name="myProject"
##ARG src_dir="myflask"
#RUN mkdir /work && mkdir /work/src && mkdir /work/tests
#
## コンテナにアクセスした際のデフォルトディレクトリ
#WORKDIR ${work_dir}

# poetryのインストール先の指定
ENV POETRY_HOME=/opt/poetry
# poetryインストール
RUN curl -sSL https://install.python-poetry.org | python && \
# シンボリックによるpathへのpoetryコマンドの追加
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
# 仮想環境を作成しない設定(コンテナ前提のため，仮想環境を作らない)
    poetry config virtualenvs.create false
# 仮想環境をprojectディレクトリで作成する
#RUN poetry config virtualenvs.in-project true

# poetryの定義ファイルをコピー (./src/配下に存在すると想定)
COPY . .
COPY .env .env

# poetryでライブラリをインストール (pyproject.tomlが既にある場合)
RUN poetry install

ENV FLASK_ENV dev


EXPOSE 5000

CMD ["poetry", "run", "gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]
