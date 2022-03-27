FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get -qy install python3 python3-dev python3-pip supervisor && \
    mkdir -p /src /var/log/supervisor /etc/supervisor/conf.d

COPY supervisor/supervisord.conf /etc/supervisor/supervisord.conf

EXPOSE 9001

ENTRYPOINT ["/usr/bin/supervisord", "-c", ""]