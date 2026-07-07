FROM python:3.13-alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN mkdir -p /repo-readme-stats/assets

ADD requirements.txt /repo-readme-stats/requirements.txt
RUN apk add --no-cache git && pip3 install -r /repo-readme-stats/requirements.txt

RUN git config --global user.name "readme-bot"
RUN git config --global user.email "41898282+github-actions[bot]@users.noreply.github.com"

ADD sources/* /repo-readme-stats/
ENTRYPOINT cd /repo-readme-stats/ && python3 main.py
