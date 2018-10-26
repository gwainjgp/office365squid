# Instructions copied from - https://hub.docker.com/_/python/
FROM python:2.7

# Instal Squid
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y squid \
 && rm -rf /var/lib/apt/lists/*


COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


ENV SQUID_VERSION=3.5.27 \
    SQUID_CACHE_DIR=/var/spool/squid \
    SQUID_LOG_DIR=/var/log/squid \
    SQUID_USER=proxy

# run the command
#CMD ["python", "./office365squid.py"]
COPY office365squid.py /etc/cron.hourly/office365squid.py
RUN chmod 755 /etc/cron.hourly/office365squid.py
RUN /etc/cron.hourly/office365squid.py

# Squid conf
COPY squid.conf /etc/squid/squid.conf

COPY entrypoint.sh /sbin/entrypoint.sh
RUN chmod 755 /sbin/entrypoint.sh

EXPOSE 3128/tcp
ENTRYPOINT ["/sbin/entrypoint.sh"]
