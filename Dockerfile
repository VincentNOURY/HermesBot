FROM python:3.10-rc-buster
WORKDIR /app
COPY . /app
RUN /usr/local/bin/python3 -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["-u", "script/main.py"]
