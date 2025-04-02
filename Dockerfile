FROM python:3.9-slim

WORKDIR /app

COPY bump_version.py /app/

RUN chmod +x /app/bump_version.py

ENTRYPOINT ["/app/bump_version.py"]
