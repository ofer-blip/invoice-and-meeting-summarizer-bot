FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY src/ $APP_HOME/
COPY docs/ $APP_HOME/docs/
COPY requirements.txt $APP_HOME/

# Install dependencies.
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir Flask gunicorn

# Run the web service on container startup.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
