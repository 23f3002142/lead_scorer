# Starting with a lightweight, official Python base image
FROM python:3.9-slim


WORKDIR /app


COPY requirements.txt .

# Installing dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of application's code 
COPY . .


EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]