#!/bin/bash

if not [ -f "/lib/tdi" ]; then
    mkdir "/lib/tdi"
fi

python ./install.py

cp ./src/* /lib/tdi
cp ./tdi.service ./lib/systemd/system/tdi.service

chmod 644 /lib/systemd/system/tdi.service
systemctl enable tdi.service
