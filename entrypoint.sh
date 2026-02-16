#!/bin/sh

set -e

echo "Waiting for postgres..."

while ! python -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.connect(('$POSTGRES_HOST', int('$POSTGRES_PORT'))); s.close()" 2>/dev/null; do
  echo "Waiting for PostgreSQL..."
  sleep 0.1
done

echo "PostgreSQL started"

exec "$@"