FROM ubuntu
RUN apt-get update && apt-get dist-upgrade -y && apt-get install -y python3 python3-pip nodejs npm && apt-get clean
WORKDIR /app
COPY . /app
RUN python3.10 -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
RUN cd Webserver
RUN npm install
RUN cd /app
CMD ["sh", "start.sh"]