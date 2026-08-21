# use a lightweight official python base image
FROM python:3.11-slim

# set working directory inside the container
WORKDIR /app

# prevent python from writing pyc fils to disc and buffering stdout and stderr for real time logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# copy and install dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy projet files into the container
COPY . .

# expose FastAPI's defaultport
EXPOSE 8000

# Defauly command to start the FastAPI web server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
