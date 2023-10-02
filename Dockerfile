FROM python:3.10
ENV PYTHONUNBUFFERED 1
RUN mkdir /requirements
ADD ./requirements /requirements
RUN pip install -r /requirements/versioned.txt

RUN mkdir /code
WORKDIR /code

# install yarn
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo """deb https://dl.yarnpkg.com/debian/ stable main""" > /etc/apt/sources.list.d/yarn.list

# install node repo
RUN #curl -sL https://deb.nodesource.com/setup_13.x | /bin/bash -

RUN apt-get clean
