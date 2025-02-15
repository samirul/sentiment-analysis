FROM python:3.12.3-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HF_HOME='/vol/model/sentiment-analysis-model'
WORKDIR /sentiment-analysis-app
COPY requirements.txt /sentiment-analysis-app/
COPY . /sentiment-analysis-app/
RUN python -m venv /virtual-py && \
    /virtual-py/bin/pip install --upgrade pip && \
    apt-get update && \
    /virtual-py/bin/pip install --no-cache-dir -r requirements.txt && \
    adduser --disabled-password sentiment-analysis-user && \
    mkdir -p /vol/model && \
    chown -R sentiment-analysis-user:sentiment-analysis-user /vol && \
    chmod -R 755 /vol

ENV PATH="/scripts:/virtual-py/bin:$PATH"

USER sentiment-analysis-user




