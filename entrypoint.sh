#!/bin/sh

for file in /iptv-api-config/*; do
  filename=$(basename "$file")
  target_file="$APP_WORKDIR/config/$filename"
  if [ ! -e "$target_file" ]; then
    cp -r "$file" "$target_file"
  fi
done

. /.venv/bin/activate

(crontab -l ; \
if [ -n "$UPDATE_CRON1" ]; then echo "$UPDATE_CRON1 cd $APP_WORKDIR && /.venv/bin/python main.py"; fi; \
if [ -n "$UPDATE_CRON2" ]; then echo "$UPDATE_CRON2 cd $APP_WORKDIR && /.venv/bin/python main.py"; fi) | crontab -

# dcron log level
# LOG_EMERG	0	[* system is unusable *]
# LOG_ALERT	1	[* action must be taken immediately *]
# LOG_CRIT	2	[* critical conditions *]
# LOG_ERR	3	[* error conditions *]
# LOG_WARNING	4	[* warning conditions *]
# LOG_NOTICE	5	[* normal but significant condition *]
# LOG_INFO	6	[* informational *]
# LOG_DEBUG	7	[* debug-level messages *]

/usr/sbin/crond -b -L /tmp/dcron.log -l 4 &

python $APP_WORKDIR/main.py &

python -m gunicorn service.app:app -b 0.0.0.0:$APP_PORT --timeout=1000
