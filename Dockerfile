FROM python:2-buster
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y git less openssh-client openssh-server gcc ffmpeg vim && rm -rf /var/lib/apt/lists/* 

COPY LambdaCast /app/

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -U setuptools
RUN pip install -r dependencies.txt

RUN yes no | python manage.py syncdb
RUN python manage.py migrate
RUN echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell
RUN python manage.py loaddata portal/fixtures/initial_data.json

EXPOSE 8000

CMD python manage.py taskd start & python manage.py runserver '0.0.0.0:8000'
