FROM python:3.11

WORKDIR /app

COPY bs_server.py .
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "bs_server.py"]
