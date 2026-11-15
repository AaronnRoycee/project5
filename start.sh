#!/bin/sh
set -e
redis-server --bind 127.0.0.1 --port 6379 --save "" --appendonly no --daemonize yes
until redis-cli -h 127.0.0.1 ping >/dev/null 2>&1; do sleep 0.2; done
exec node /app/word-count-app/server.js
