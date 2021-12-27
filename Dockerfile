FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1

EXPOSE 8000
WORKDIR /app


RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY ./requiremets.txt /app/requiremets.txt

COPY . ./
RUN pip install --no-cache-dir --upgrade -r /app/requiremets.txt

CMD alembic upgrade head && \
    uvicorn --host=0.0.0.0 app.main:app --reload
