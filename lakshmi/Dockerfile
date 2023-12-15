FROM python:3.9-slim AS builder

WORKDIR /app

# Virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONPATH "${PYTHONPATH}:/"

COPY ./app /app
COPY ./requirements.txt /app

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade -r requirements.txt

FROM builder
COPY --from=builder /app /app
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

CMD ["python", "main.py"]
