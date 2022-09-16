FROM python:3.10
WORKDIR /home

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY src ./
COPY .env ./

CMD ["python", "bot.py"]
