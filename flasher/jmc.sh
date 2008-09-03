#!/bin/sh
for f in jmc_*xml; do 
    echo anvil start -f $f flasher
    echo sleep 270
    echo anvil start flasher
    echo sleep 15
done
