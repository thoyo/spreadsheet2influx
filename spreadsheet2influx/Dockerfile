FROM python:3.8

ENV SPREADSHEET2INFLUX /opt/spreadsheet2influx

RUN mkdir -p $SPREADSHEET2INFLUX
WORKDIR $SPREADSHEET2INFLUX

COPY requirements.txt .
COPY service_account.json .
RUN pip install -r requirements.txt

ENV AM_I_IN_A_DOCKER_CONTAINER Yes

COPY .env .
COPY main.py .

CMD ["python", "-u", "main.py"]

