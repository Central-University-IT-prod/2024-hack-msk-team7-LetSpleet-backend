FROM python:3.12-slim

COPY . .

RUN pip install --no-cache-dir -r requirements.txt


ENV PYTHONPATH "${PYTHONPATH}:/backend"

EXPOSE 4000

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "4000"]
