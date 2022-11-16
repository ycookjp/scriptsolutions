FROM python:3-alpine
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN python3 -m pip install -r polls/requirements.txt \
 && rm -f db.sqlite3 \
 && python3 manage.py migrate \
 && python3 initdb.py
