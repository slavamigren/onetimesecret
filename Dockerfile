FROM python:3

WORKDIR /app

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . /app/

COPY ./entrypoint /

RUN sed -i 's/\r$//g' /entrypoint

RUN chmod u+x /entrypoint

ENTRYPOINT ["/entrypoint"]