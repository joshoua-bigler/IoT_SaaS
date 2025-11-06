FROM python:3.12.5
# prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# dependencies -----------------------------------------------------------
WORKDIR /app
COPY db_manager /app/db_manager
COPY pyproject.toml /app
RUN pip install --upgrade pip
RUN pip install /app/
# start the app ----------------------------------------------------------
CMD ["python3", "/app/stdpe_api/main.py"]