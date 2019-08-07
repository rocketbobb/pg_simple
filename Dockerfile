FROM python:3.7-alpine

RUN apk add --update curl gcc g++ git \
    && rm -rf /var/cache/apk/*

RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# RUN pip install https://github.com/wangsha/loggly-python-handler/archive/master.zip

COPY . /app

RUN apk add --no-cache bash

# change to db-setup.sh 
RUN chmod +x boot.sh

ENTRYPOINT ["boot.sh"]