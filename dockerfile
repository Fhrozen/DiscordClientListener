FROM python:3.11-alpine

COPY discord_client.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

ENV DIFY_API_URL=http://localhost/v1
# ENV DIFY_API_URL
# ENV DIFY_API_KEY

ENTRYPOINT [ "python", "discord_client.py" ]
