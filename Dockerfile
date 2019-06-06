FROM ubuntu

WORKDIR /root

RUN apt-get update \
    && apt-get install -y \
    python3 \
    python3-pip\
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . /root/

RUN pip3 install -r requirements.txt

ENV GOOGLE_APPLICATION_CREDENTIALS=/root/cached_translations-f927008f4f77.json
ENV ENV=docker

CMD ["python3", "cached_translation_server.py"]