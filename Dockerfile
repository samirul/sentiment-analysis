FROM python:3.12.3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HF_HOME='sentiment-analysis-model/model/'
EXPOSE 5001
EXPOSE 5002
EXPOSE 5003
EXPOSE 5004
WORKDIR /sentiment-analysis-app
COPY requirements.txt /sentiment-analysis-app/
COPY . /sentiment-analysis-app/
COPY scripts.sh .
RUN python -m venv /virtual-py && \
    /virtual-py/bin/pip install --upgrade pip && \
    apt-get update && \
    /virtual-py/bin/pip install --no-cache-dir -r requirements.txt && \
    adduser --disabled-password sentiment-analysis-user && \
    chown -R sentiment-analysis-user:sentiment-analysis-user /sentiment-analysis-app && \
    chmod -R 755 /sentiment-analysis-app && \
    chmod +x scripts.sh


USER sentiment-analysis-user

CMD ["./scripts.sh"]




