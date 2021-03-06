FROM python:slim

WORKDIR /usr/src/app

ENV TG_BOT_TOKEN TOKEN
ENV MCRCON_HOST localhost
ENV MCRCON_PASS minecraft

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .

CMD [ "python", "./rminecraft.py" ]
