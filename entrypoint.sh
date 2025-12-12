#!/bin/sh
set -e

for file in /iptv-api-config/*; do
  filename=$(basename "$file")
  target_file="$APP_WORKDIR/config/$filename"
  if [ ! -e "$target_file" ]; then
    cp -r "$file" "$target_file"
  fi
done

. /.venv/bin/activate

: "${APP_PORT:=$APP_PORT}"
: "${NGINX_HTTP_PORT:=$NGINX_HTTP_PORT}"
: "${NGINX_RTMP_PORT:=$NGINX_RTMP_PORT}"

sed -e "s/\${APP_PORT}/${APP_PORT}/g" \
    -e "s/\${NGINX_HTTP_PORT}/${NGINX_HTTP_PORT}/g" \
    -e "s/\${NGINX_RTMP_PORT}/${NGINX_RTMP_PORT}/g" \
    /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

nginx -g 'daemon off;' &

python $APP_WORKDIR/main.py &

python -m gunicorn service.app:app -b 0.0.0.0:$APP_PORT --timeout=1000
