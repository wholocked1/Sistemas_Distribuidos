FROM python:3.9-slim

WORKDIR /server

COPY requirements.txt requirements.txt

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY testeip.py testeip.py

CMD ["python", "testeip.py"]