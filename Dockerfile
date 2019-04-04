FROM python:3.6
MAINTAINER Hiram <jie.zhang8@luckyair.net>

RUN mkdir /myapp
WORKDIR /myapp
COPY app /myapp/app
COPY entrypoint.sh /myapp/
COPY wsgi.py /myapp/
COPY requirements.txt /myapp/

RUN pip install -r requirements.txt && pip install uwsgi
RUN chmod +x entrypoint.sh

EXPOSE 5000

CMD ["/myapp/entrypoint.sh"]