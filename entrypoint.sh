#!/bin/bash
# The script starts as the root inside the container to correct the folder permissions.
chown -R rethinkdb:rethinkdb /data

# Here the script starts the database inside of the container
exec gosu rethinkdb rethinkdb --bind all
