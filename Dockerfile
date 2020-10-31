FROM ubuntu:18.04
MAINTAINER alalmironow@gmail.com

RUN apt-get update
RUN apt install -y software-properties-common
RUN add-apt-repository ppa:jonathonf/ffmpeg-4
RUN apt-get update
RUN apt-get -y install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
RUN apt-get -y install ffmpeg
RUN apt-get -y install python3.7 
RUN apt-get -y install python3-pip

#Copy requirements Python3
COPY requirements.txt /requirements.txt
COPY daemon.py /daemon.py
#Copy crontab file
COPY start.sh /start.sh
RUN chmod +x /start.sh
#Create bots dir
RUN mkdir /bots
COPY bots/ /bots

#Pip install libs
RUN pip3 install --no-cache-dir -r /requirements.txt
# Create the log file to be able to run tail
RUN touch /var/log/telegram_bots.log
# Run the command on container startup

CMD ./start.sh
