#!/bin/sh
set -eux

./scripts/post_deploy.sh

# Get env vars in the Dockerfile to show up in the SSH session
# See also: https://azureossd.github.io/2022/04/27/2022-Enabling-SSH-on-Linux-Web-App-for-Containers/index.html
eval $(printenv | sed -n "s/^\([^=]\+\)=\(.*\)$/export \1=\2/p" | sed 's/"/\\\"/g' | sed '/=/s//="/' | sed 's/$/"/' >> /etc/profile)

service ssh start
exec "$@"
