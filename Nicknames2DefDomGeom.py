#!/usr/bin/env python
#
# Use nicknames.txt file to create a default-dom-geometry file and print the
# result to sys.stdout

from DefaultDomGeometry import NicknameReader

if __name__ == "__main__":
    # read in default-dom-geometry.xml
    #defDomGeom = DefaultDomGeometryReader().read()

    defDomGeom = NicknameReader().read()

    # rewrite the 64-DOM strings to 60 DOM strings plus 32 DOM icetop hubs
    defDomGeom.rewrite()

    # dump the new default-dom-geometry data to sys.stdout
    defDomGeom.dump()
