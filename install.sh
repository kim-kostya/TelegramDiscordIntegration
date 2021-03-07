#!/bin/bash

useradd -r tdi

mkdir "/lib/tdi"
mkdir "/etc/tdi/"

python3 ./install.py
chmod +x /etc/profile.d/tdi_environment.sh

python3 -m venv /lib/tdi/tdi_venv

chmod +x /lib/tdi/tdi_venv/bin/activate
/lib/tdi/tdi_venv/bin/activate

/lib/tdi/tdi_venv/bin/python -m pip install -U discord.py
/lib/tdi/tdi_venv/bin/python -m pip install -U pyTelegramBotAPI
/lib/tdi/tdi_venv/bin/python -m pip install -U psycopg2
/lib/tdi/tdi_venv/bin/python -m pip install -U requests

cp ./src/* /lib/tdi
cp ./tdi.service /lib/systemd/system/tdi.service

chown tdi /lib/tdi
chown tdi /etc/tdi

chmod +x /lib/tdi/start.sh

chmod 644 /lib/systemd/system/tdi.service
systemctl enable tdi.service
reload
