FROM python:3.9
RUN mkdir -p /usr/src/app
COPY . /usr/src/app

WORKDIR /usr/src/app
RUN python -m pip install -r requirements.txt
CMD ["/usr/src/app/start.sh"]