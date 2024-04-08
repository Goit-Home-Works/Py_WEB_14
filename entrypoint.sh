#!/bin/sh
set -e

# Change permissions of mounted volume
chmod -R a+rwx /var/lib/postgresql/data

# Run the CMD passed to the entrypoint
exec "$@"
