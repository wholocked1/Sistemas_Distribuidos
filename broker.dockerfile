FROM python:latest

# WORKDIR /server

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY broker.py broker.py

CMD ["python", "servidor3.py"]