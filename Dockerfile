FROM python:2-buster
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y git less openssh-client openssh-server gcc ffmpeg && rm -rf /var/lib/apt/lists/* 

COPY LambdaCast /app/

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -U setuptools
RUN pip install -r dependencies.txt

RUN yes no | python manage.py syncdb
RUN python manage.py migrate
RUN echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell
RUN echo "from portal import models; models.Channel.objects.create(name='LinuxLounge', description='Dies ist eine Beschreibung.', featured=True)" | python manage.py shell
RUN echo 'from portal import models; models.Submittal.objects.create(title="LinuxLounge", description="Dies ist eine Beschreibung der Vorlage.", media_title="LL2XX", media_description="In dieser Folge der LinuxLounge geht es um...", media_linkURL="https://theradio.cc/blog/2023/02/12/ll266-mein-linux-saugt/", media_mp3URL="https://rec.theradio.cc/auphonic/20230212_linuxlounge266.mp3", media_audioThumbURL="https://rec.theradio.cc/media/thumbnails/LinuxLounge.png", media_published=True)' | python manage.py shell
#RUN echo "from django.contrib.auth.models import User; User.objects.get(username='admin')"

EXPOSE 8000

CMD python manage.py taskd start & python manage.py runserver '0.0.0.0:8000'
