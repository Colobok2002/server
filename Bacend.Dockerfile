FROM python:3.12-slim

RUN pip install poetry

RUN poetry config virtualenvs.create false

WORKDIR /app
COPY pyproject.toml /app/
RUN poetry install --no-root

COPY . /app

EXPOSE 8080

CMD ["uvicorn", "sql_training.rest.run:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
