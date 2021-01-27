FROM python:3.8.1

ENV APP_HOME=/econ
ENV FLASK_APP=econ.py
ENV FLASK_RUN_HOST=0.0.0.0

WORKDIR $APP_HOME

COPY . /econ

RUN pip install -r requirements.txt
