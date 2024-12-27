FROM python:3.12-slim as builder

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-dev

COPY . .

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
