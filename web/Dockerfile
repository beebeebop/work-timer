FROM python:3.6-slim

# Create the group and user to be used in this container
RUN groupadd flaskgroup && useradd -m -g flaskgroup -s /bin/bash flask

# Create the working directory (and set it as the working directory)
RUN mkdir -p /home/flask/app/web
WORKDIR /home/flask/app/web


# Install the package dependencies 
#COPY requirements.txt /home/flask/app/web
#RUN pip install --no-cache-dir -r requirements.txt

COPY requirements_freezed.txt /home/flask/app/web
RUN pip install --no-cache-dir -r requirements_freezed.txt


# Copy the source code into the container
COPY . /home/flask/app/web

RUN chown -R flask:flaskgroup /home/flask

USER flask
