FROM python:3.11-slim

WORKDIR /docs

COPY . /docs

RUN pip install --no-cache-dir --upgrade -r /docs/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5555"]
