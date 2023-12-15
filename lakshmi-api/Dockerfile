FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y iputils-ping net-tools vim telnet

# Virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONPATH "${PYTHONPATH}:/"

COPY ./requirements.txt /app
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
