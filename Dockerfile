
FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /todoAPI
WORKDIR /todoAPI
COPY requirements.txt /todoAPI/
RUN pip install -r requirements.txt
COPY . /todoAPI/

