FROM python:3.9
COPY requirements.txt .
RUN apt update && apt upgrade -y
RUN apt install rabbitmq-server && rabbitmq-plugins enable rabbitmq_management

RUN pip install -r requirements.txt

WORKDIR /anaraiza

COPY ./static ./static
COPY .env .
COPY config.ini .
COPY main.py .
COPY proxy.csv .
COPY ./modules ./modules

ENV PATH=/root/.local:$PATH

CMD [ "python", "-u", "./main.py"]