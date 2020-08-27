FROM python:3.7.2-stretch
# set work directory
WORKDIR /app
ADD . /app

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["uwsgi", "app.ini"]
