FROM python:latest

ADD servidor1.py .

COPY . .

RUN set -xe \
    && python3 -m venv env \
    && source env/bin/activate \
    && pip install \
    && pip install -r requirements.txt





CMD [ "python", "./servidor1.py" ]