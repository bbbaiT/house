FROM python:3.6
WORKDIR /app

COPY ./requirements.txt .

RUN pip install -r requirements.txt \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone

COPY . .

EXPOSE 8000
#CMD ["gunicorn", "manage:app", "-c", "./gunicorn.conf.py"]
