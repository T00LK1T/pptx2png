FROM python:3.12.7-slim-bullseye

RUN pip install poetry==1.8.2
RUN sed -i 's/main$/main contrib non-free/g' /etc/apt/sources.list && \
    apt update -y && \
    apt install -y --no-install-recommends \
        curl procps tree make \
        libreoffice  default-jre \
        poppler-utils \
        fonts-crosextra-carlito fonts-crosextra-caladea fonts-croscore \
        fonts-noto-cjk \
        ttf-mscorefonts-installer \
        fontconfig && \
    apt clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /d3fau1t/app

WORKDIR /d3fau1t/app

COPY . .
# 외부 폰트파일 필요한경우
# COPY ./fonts/NotoSansJP-Regular.otf /usr/share/fonts/opentype/

RUN poetry config virtualenvs.in-project true && \
    poetry config cache-dir /d3fau1t/app/.cache && \
    poetry install --only=main

RUN fc-cache -fv

RUN groupadd -g 1000 d3fau1t && \
    useradd -u 1000 -g d3fau1t -d /d3fau1t/app -m -s /bin/bash d3fau1t && \
    chown -R d3fau1t:d3fau1t /d3fau1t

USER d3fau1t
