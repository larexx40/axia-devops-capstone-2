# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STAGE 1: builder
# Full Python image with all dev tools
# Runs linting and tests here
# If tests fail — image never builds
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -m flake8 app.py database.py utils.py config.py test_app.py
RUN python -m pytest test_app.py -v


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STAGE 2: production
# Minimal slim image — no dev tools
# pytest and flake8 are NOT included
# Runs as non-root user for security
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FROM python:3.11-slim AS production

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir \
    Flask==3.1.0 \
    boto3==1.34.0 \
    Werkzeug==3.1.0 \
    python-dotenv==1.0.0

COPY app.py .
COPY config.py .
COPY database.py .
COPY utils.py .

RUN useradd --no-create-home --shell /bin/false appuser
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c \
    "import urllib.request; \
    urllib.request.urlopen('http://localhost:5000/health')" \
    || exit 1

CMD ["python", "app.py"]
