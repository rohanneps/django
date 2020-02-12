#8 Dockerfile - this is a comment. Delete me if you want.
FROM python:3.6

RUN mkdir -p /app/rest_image_match_server
COPY requirements.txt /app/requirements.txt

RUN apt-get -y update && apt-get install -y build-essential

# installing python, pip and virtualenv
#RUN apt-get install -y --no-install-recommends python3.6
RUN apt-get -y --no-install-recommends install python3-pip && pip3 install virtualenv 

# For python mysql interface
RUN apt-get install -y --no-install-recommends python-dev python3-dev default-libmysqlclient-dev

# For opencv
RUN apt-get install -y --no-install-recommends libglib2.0-0 libsm6 libxext6 libxrender1

WORKDIR /app/rest_image_match_server
RUN virtualenv -p python3 /app/venv

RUN /app/venv/bin/pip install --no-cache-dir -r /app/requirements.txt

ENV rest_server_host_address=

EXPOSE 8000
