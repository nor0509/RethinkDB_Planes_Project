FROM rethinkdb:latest

RUN apt-get update && apt-get install -y gosu dos2unix && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /usr/local/bin/

RUN dos2unix /usr/local/bin/entrypoint.sh && chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]