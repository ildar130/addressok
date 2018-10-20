FROM ubuntu:14.04.1
MAINTAINER Ildar Ahmadullin <ildar.130@gmail.com>

RUN echo 'deb http://archive.ubuntu.com/ubuntu/ trusty-security multiverse' \
	>> /etc/apt/sources.list.d/multiverse.list

# Installing packages
RUN apt-get update && apt-get -y install\
	nginx\
	libxml2-dev\
	libxslt1-dev\
	python3\
	python3-dev\
	python3-lxml\
	python3-pip\
	wget\
	unrar\
	&& apt-get clean

RUN echo "alias python='python3'" >> /root/.bashrc
RUN echo "alias pip='pip3'" >> /root/.bashrc

RUN pip3 install flask==0.10.1
RUN pip3 install --upgrade pip
RUN pip3 install PyMySQL\
	&& pip3 install uwsgi

RUN mkdir /conf
RUN mkdir /logs
VOLUME ["/conf", "/logs"]
COPY nginx.conf /conf/nginx.conf
COPY uwsgi.ini /conf/uwsgi.ini
RUN touch /app_socket.sock
RUN chown www-data:www-data /app_socket.sock
RUN ln -sf /conf/nginx.conf /etc/nginx/nginx.conf

EXPOSE 14000

ADD entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]
