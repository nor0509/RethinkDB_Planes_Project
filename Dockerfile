# The dockerfile inserts the entrypoint.sh into the rethinkdb image. The goal was to correct the permission before going forward
FROM rethinkdb:latest
COPY entrypoint.sh /usr/local/bin/
RUN apt-get update && apt-get install -y gosu && rm -rf /var/lib/apt/lists/*
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]