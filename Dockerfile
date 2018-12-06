FROM python:3.6

EXPOSE 8000

RUN mkdir /opt/logging /opt/images /opt/running /opt/app_files && apt install curl -y

COPY src/ /opt/app

WORKDIR /opt/app

RUN pip install -r /opt/app/requirements.txt