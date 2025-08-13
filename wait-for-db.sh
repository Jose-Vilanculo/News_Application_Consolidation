#!/bin/sh

# Wait until MySQL is accepting connections
echo "⏳ Waiting for MySQL at $DB_HOST:$DB_PORT..."

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done

echo "✅ Database is up – starting Django!"

exec "$@"
