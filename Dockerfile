FROM python:latest

WORKDIR /server

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY servidor1.py servidor1.py

CMD ["python"]