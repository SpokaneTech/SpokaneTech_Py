#!/bin/sh
set -eux
service ssh start
exec "$@"
