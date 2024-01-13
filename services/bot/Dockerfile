FROM nikolaik/python-nodejs:latest

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN npm install -g nodemon
COPY ./src /code/src
COPY .env /code/.env
