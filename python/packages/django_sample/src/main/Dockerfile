FROM python:3-alpine
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN python3 -m pip install -r mycalendar/requirements.txt \
 && rm -f db.sqlite3 \
 && python3 manage.py migrate
