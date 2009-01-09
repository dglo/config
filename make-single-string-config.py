#!/usr/bin/env python

# makeconfig
# John Jacobsen, NPX Designs, Inc., john@mail.npxdesigns.com
# Started: Wed Jan 16 23:54:00 2008

import optparse


def doconfig(string):

    configtxt = """<?xml version="1.0" encoding="UTF-8"?>
<runConfig>
    <domConfigList>sps-%si-lc2-slc-002</domConfigList>
    <triggerConfig>sps-icecube-amanda-008</triggerConfig>
    <runComponent name="inIceTrigger"/>
    <runComponent name="globalTrigger"/>
    <runComponent name="eventBuilder"/>
    <runComponent name="secondaryBuilders"/>
</runConfig>
"""
    filename = "sps-stringtest-2-%s.xml"
    filename  = filename % string
    configtxt = configtxt % string
    out = file(filename, "w")
    print >>out, configtxt
    out.close()

def main():
    p = optparse.OptionParser()
    opt, args = p.parse_args()
    for string in args:
        doconfig(string)
    
if __name__ == "__main__": main()

