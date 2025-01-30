FROM pytorch/pytorch:2.6.0-cuda11.8-cudnn9-runtime

RUN mkdir -p /app/src

RUN addgroup --system python && adduser --system --group python
RUN chown -R python:python /app
USER python

ENV VIRTUAL_ENV=/app/.venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip --default-timeout=1000 install -r requirements.txt

WORKDIR /app
COPY --chown=python:python ./src/. ./src
COPY --chown=python:python ./models/. ./models/
RUN mkdir -p data
RUN python src/download_models.py

ENV PYTHONPATH "${PYTHONPATH}:/app/src"
