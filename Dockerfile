FROM python:3.8
LABEL authors="Zhang Jing Yu"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV APP_HOME=/code
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

ENV POST_DB_HOST='39.108.75.181'
ENV REDIS_URL=''

COPY . $APP_HOME

RUN /usr/local/bin/python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

EXPOSE 8000

CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8000"]
