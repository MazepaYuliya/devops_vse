FROM python:3.11-slim

WORKDIR /docs

COPY . /docs

RUN pip install --no-cache-dir --upgrade -r /docs/requirements.txt

CMD ["python", "bot.py"]
