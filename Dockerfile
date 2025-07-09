FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the Phi-3 model during build (saves startup time)
RUN python -c "from transformers import AutoModel; AutoModel.from_pretrained('microsoft/Phi-3-mini-4k-instruct')"

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "optiforce_app:app"]
