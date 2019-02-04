cat << EOF >> /etc/crontab

00 02 * * * root python3 /home/backup.py

