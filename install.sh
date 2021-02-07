#!/bin/bash

if not [ -f "/lib/tdi" ]; then
    mkdir "/lib/tdi"
fi

cp ./src/* /lib/tdi
cp tdi.service