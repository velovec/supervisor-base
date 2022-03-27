FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get -qy install python3 python3-dev python3-pip supervisor cron && \
    mkdir -p /src/agent /var/log/supervisor /etc/supervisor/conf.d

COPY supervisor/supervisord.conf /etc/supervisor/supervisord.conf
COPY supervisor/crontab /etc/crontab

COPY src/* /src/agent/

EXPOSE 9001

ENTRYPOINT ["/usr/bin/supervisord"]
CMD ["-c", "/etc/supervisor/supervisord.conf"]