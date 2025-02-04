# start from python base image
FROM python:3.10-slim

# change working directory on docker image
WORKDIR /app

# add requirements file to docker image
COPY ./requirements.txt /app/requirements.txt

# install python libraries
RUN pip install --no-cache-dir -r /app/requirements.txt

# add python code to docker image
COPY ./ /app/

# specify default commands
CMD ["python", "/app/main.py"]