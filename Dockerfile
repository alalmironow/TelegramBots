FROM ubuntu:18.04
MAINTAINER alalmironow@gmail.com

RUN apt-get update
RUN apt install -y software-properties-common
RUN add-apt-repository ppa:jonathonf/ffmpeg-4
RUN apt-get update
RUN apt-get -y install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
RUN apt-get -y install ffmpeg
RUN apt-get -y install cron
RUN apt-get -y install python3.7 
RUN apt-get -y install python3-pip

RUN mkdir /app

#Copy requirements Python3
COPY requirements.txt /app/requirements.txt
COPY daemon.py /app/daemon.py
#Copy crontab file
COPY crontab.txt /app/crontab.txt
#Create bots dir
RUN mkdir /app/bots
COPY bots/ /app/bots

#Pip install libs
RUN pip3 install --no-cache-dir -r /app/requirements.txt
# Apply cron job
RUN crontab /app/crontab.txt
# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the command on container startup
CMD cron && tail -f /var/log/cron.log