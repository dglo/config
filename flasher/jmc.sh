#!/bin/sh
for f in jmc_*xml; do 
    /usr/local/pdaq/anvil/anvil start -f $f flasher
    sleep 270
    /usr/local/pdaq/anvil/anvil start flasher
    sleep 25
done
