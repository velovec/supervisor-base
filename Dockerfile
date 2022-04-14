FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get -qy install python3 python3-dev python3-pip python3-requests supervisor && \
    mkdir -p /src/agent /var/log/supervisor /etc/supervisor/conf.d

COPY supervisor/supervisord.conf /etc/supervisor/supervisord.conf

COPY src/agent/ /src/agent/
RUN chmod +x /src/agent/main.py

EXPOSE 9001

ENTRYPOINT ["/usr/bin/supervisord"]
CMD ["-c", "/etc/supervisor/supervisord.conf"]