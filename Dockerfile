FROM ubuntu:latest
MAINTAINER alalmironow@gmail.com

RUN apt-get update && apt-get -y install cron && apt-get -y install python3.7 && apt-get -y install python3-pip

RUN mkdir /app

#Copy requirements Python3
COPY requirements.txt /app/requirements.txt

#Pip install libs
RUN pip3 install --no-cache-dir -r /app/requirements.txt

#Copy crontab file
COPY crontab.txt /app/crontab.txt

# Apply cron job
RUN crontab /app/crontab.txt

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

#Create bots dir
RUN mkdir /app/bots

COPY bots/ /app/bots

# Run the command on container startup
CMD cron && tail -f /var/log/cron.log