#!/usr/bin/env python
#
# Rewrite the default-dom-geometry file from 64 DOMs per in-ice string to
# 60 DOMs per in-ice string and 32 DOMs per icetop hub and print the
# result to sys.stdout

import os, os.path, sys, traceback

from xml.dom import minidom, Node

class ProcessError(Exception): pass
class BadFileError(Exception): pass

class XMLParser(object):
    def getChildNode(cls, node, childName, hasAttr=False, hasKids=True):
        """
        Get the child node which has the specified name.
        Will also verify that the child node does not have any attributes
        and has its own child nodes -- this check can be changed by setting
        'hasAttr' or 'hasKids' to the appropriate boolean value, or disabled
        by setting the value to None
        """
        nodeName = '<%s>' % str(node.nodeName)
        if nodeName == '<#document>':
            nodeName = 'top-level'

        if node.childNodes is None or len(node.childNodes) == 0:
            raise ProcessError('No %s child nodes' % nodeName)

        # find first child node which matches the specified name
        #
        child = None
        for kid in node.childNodes:
            if kid.nodeType == Node.TEXT_NODE:
                continue

            if kid.nodeType == Node.COMMENT_NODE:
                continue

            if kid.nodeType == Node.ELEMENT_NODE and kid.nodeName == childName:
                if child is not None:
                    raise ProcessError('Found multiple copies of %s node <%s>' %
                                       (nodeName, kid.nodeName))
                child = kid
                continue

            raise ProcessError('Found unknown %s node <%s>' %
                               (nodeName, kid.nodeName))

        if child is None:
            raise ProcessError('No <%s> child node for %s' %
                               (childName, nodeName))

        if hasAttr is not None:
            if hasAttr:
                if child.attributes is None or len(child.attributes) == 0:
                    raise ProcessError('<%s> node has no attributes' %
                                       childName)
            elif child.attributes is not None and len(child.attributes) > 0:
                raise ProcessError('<%s> node has unexpected attributes' %
                                   childName)

        if hasKids is not None:
            if hasKids:
                if child.childNodes is None or len(child.childNodes) == 0:
                    raise ProcessError('<%s> node has no children' % childName)
            elif child.childNodes is not None and len(child.childNodes) > 0:
                raise ProcessError('<%s> node has unexpected children' %
                                   childName)

        return child
    getChildNode = classmethod(getChildNode)

    def getChildText(cls, node):
        "Return the text from this node's child"
        nodeName = '<%s>' % str(node.nodeName)
        if nodeName == '<#document>':
            nodeName = 'top-level'

        if node.childNodes is None or len(node.childNodes) == 0:
            raise ProcessError('No %s child nodes' % nodeName)

        text = None
        for kid in node.childNodes:
            if kid.nodeType == Node.TEXT_NODE:
                if text is not None:
                    raise ProcessError('Found multiple %s text nodes' %
                                       nodeName)
                text = kid.nodeValue
                continue

            if kid.nodeType == Node.COMMENT_NODE:
                continue

            if kid.nodeType == Node.ELEMENT_NODE:
                raise ProcessError('Unexpected %s child <%s>' %
                                   (node.nodeName, kid.nodeName))

            raise ProcessError('Found unknown %s node <%s>' %
                               (nodeName, kid.nodeName))

        if text is None:
            raise ProcessError('No text child node for %s' % nodeName)

        return text
    getChildText = classmethod(getChildText)

class Dom(XMLParser):
    "Data for a single DOM"
    def __init__(self, string, node):
        "Extract a single DOM's data from the default-dom-geometry XML tree"
        if node.attributes is not None and len(node.attributes) > 0:
            raise ProcessError('<%s> node has unexpected attributes' %
                               node.nodeName)

        self.string = string

        self.pos = None
        self.id = None
        self.name = None
        self.prod = None
        self.x = None
        self.y = None
        self.z = None

        for kid in node.childNodes:
            if kid.nodeType == Node.TEXT_NODE:
                continue

            if kid.nodeType == Node.COMMENT_NODE:
                continue

            if kid.nodeType == Node.ELEMENT_NODE:
                if kid.nodeName == 'position':
                    self.pos = int(self.getChildText(kid))
                elif kid.nodeName == 'mainBoardId':
                    self.id = self.getChildText(kid)
                elif kid.nodeName == 'name':
                    self.name = self.getChildText(kid)
                elif kid.nodeName == 'productionId':
                    self.prod = self.getChildText(kid)
                elif kid.nodeName == 'xCoordinate':
                    self.x = float(self.getChildText(kid))
                elif kid.nodeName == 'yCoordinate':
                    self.y = float(self.getChildText(kid))
                elif kid.nodeName == 'zCoordinate':
                    self.z = float(self.getChildText(kid))
                else:
                    raise ProcessError('Unexpected %s child <%s>' %
                                       (node.nodeName, kid.nodeName))
                continue

            raise ProcessError('Found unknown %s node <%s>' %
                               (node.nodeName, kid.nodeName))

        if self.pos is None:
            if self.name is not None:
                dname = self.name
            elif id is None:
                dname = self.id
            else:
                raise ProcessError('Blank DOM entry')

            raise ProcessError('DOM %s is missing ID in string %s' % dname)
        if self.id is None:
            raise ProcessError('DOM pos %d is missing ID in string %s' %
                               (self.pos, self.string))
        if self.name is None:
            raise ProcessError('DOM %s is missing ID in string %s' % self.id)

    def __str__(self):
        return '%s[%s] %02d-%02d' % (self.id, self.name, self.string, self.pos)

    def getId(self): return self.id
    def getName(self): return self.name
    def getPos(self): return self.pos
    def getString(self): return self.string

class DefaultDomGeometry(XMLParser):
    def __init__(self, fileName=None):
        "Read in the default-dom-geometry data"
        if fileName is None:
            if not os.environ.has_key('PDAQ_HOME'):
                raise ProcessError('No PDAQ_HOME environment variable')

            fileName = os.path.join(os.environ['PDAQ_HOME'], 'config',
                                    'default-dom-geometry.xml')

        if not os.path.exists(fileName):
            raise BadFileError('Cannot read default dom geometry file "%s"' %
                               fileName)

        try:
            dom = minidom.parse(fileName)
        except Exception, e:
            raise ProcessError("Couldn't parse \"%s\": %s" % (fileName, str(e)))

        geom = self.getChildNode(dom, 'domGeometry')

        self.stringToDom = {}
        self.domIdToDom = {}
        for kid in geom.childNodes:
            if kid.nodeType == Node.TEXT_NODE:
                continue

            if kid.nodeType == Node.COMMENT_NODE:
                continue

            if kid.nodeType == Node.ELEMENT_NODE:
                if kid.nodeName == 'string':
                    self.__parseStringGeometry(kid)
                else:
                    raise ProcessError('Unknown domGeometry node <%s>' %
                                       kid.nodeName)
                continue

            raise ProcessError('Found unknown domGeometry node <%s>' %
                               kid.nodeName)

    def __parseStringGeometry(self, node):
        "Extract data from a default-dom-geometry <string> node tree"
        if node.attributes is not None and len(node.attributes) > 0:
            raise ProcessError('<%s> node has unexpected attributes' %
                               node.nodeName)

        stringNum = None
        for kid in node.childNodes:
            if kid.nodeType == Node.TEXT_NODE:
                continue

            if kid.nodeType == Node.COMMENT_NODE:
                continue

            if kid.nodeType == Node.ELEMENT_NODE:
                if kid.nodeName == 'number':
                    stringNum = int(self.getChildText(kid))
                    if self.stringToDom.has_key(stringNum):
                        errMsg = 'Found multiple entries for string %d' % \
                            stringNum
                        raise ProcessError(errMsg)
                    self.stringToDom[stringNum] = []
                elif kid.nodeName == 'dom':
                    if stringNum is None:
                        raise ProcessError('Found <dom> before <number>' +
                                           ' under <string>')
                    dom = Dom(stringNum, kid)
                    self.stringToDom[stringNum].append(dom)

                    mbId = dom.id
                    if self.domIdToDom.has_key(mbId):
                        oldNum = self.domIdToDom[mbId].getString()
                        print >>sys.stderr, ('DOM %s belongs to both' +
                                             ' string %d and %d') % \
                                             (mbid, oldNum, stringNum)
                    self.domIdToDom[mbId] = dom
                else:
                    raise ProcessError('Unexpected %s child <%s>' %
                                       (node.nodeName, kid.nodeName))
                continue

            raise ProcessError('Found unknown %s node <%s>' %
                               (node.nodeName, kid.nodeName))

        if stringNum is None:
            raise ProcessError('String is missing number')

    def getDomIdToDomDict(self):
        "Get the DOM mainboard ID -> DOM object dictionary"
        return self.domIdToDom

    def getStringToDomDict(self):
        "Get the string number -> DOM object dictionary"
        return self.stringToDom

def dump(stringToDom):
    "Dump the string->DOM dictionary in default-dom-geometry format"
    strList = stringToDom.keys()
    strList.sort()

    print '<?xml version="1.0"?>'
    print '<domGeometry>'
    for s in strList:
        print '   <string>'
        print '      <number>%02d</number>' % s
        for dom in stringToDom[s]:
            print '     <dom>'
            if dom.pos is not None:
                if s % 1000 == 1:
                    print '        <position>%d</position>' % dom.pos
                else:
                    print '        <position>%02d</position>' % dom.pos
            if dom.id is not None:
                print '        <mainBoardId>%s</mainBoardId>' % dom.id
            if dom.name is not None:
                print '        <name>%s</name>' % dom.name
            if dom.prod is not None:
                print '        <productionId>%s</productionId>' % dom.prod
            if dom.x is not None:
                print '        <xCoordinate>%4.2f</xCoordinate>' % dom.x
            if dom.y is not None:
                print '        <yCoordinate>%4.2f</yCoordinate>' % dom.y
            if dom.z is not None:
                print '        <zCoordinate>%4.2f</zCoordinate>' % dom.z
            print '     </dom>'

        print '   </string>'
    print '</domGeometry>'

def getIcetopNum(strNum):
    "Translate the in-ice string number to the corresponding icetop hub"
    if strNum % 1000 == 0 or strNum > 2000: return strNum
    if strNum > 1000: return ((((strNum - 1000) + 7)) / 8) + 1080
    # SPS map goes here
    if strNum in [46, 55, 56, 65, 72, 73, 77, 78]: return 81
    if strNum in [38, 39, 48, 58, 64, 66, 71, 74]: return 82
    if strNum in [30, 40, 47, 49, 50, 57, 59, 67]: return 83
    if strNum in [21, 29]: return 84
    if strNum in [45, 54, 62, 63, 69, 70, 75, 76]: return 85
    if strNum in [44, 52, 53, 60, 61, 68]: return 86
    raise ProcessError('Bad in-ice string %d' % strNum)

def rewrite(stringToDom):
    """
    Rewrite default-dom-geometry from 64 DOMs per string hub to
    60 DOMs per string hub and 32 DOMs per icetop hub
    """
    strList = stringToDom.keys()
    strList.sort()

    for s in strList:
        domList = stringToDom[s]

        idx = 0
        while idx < len(domList):
            dom = domList[idx]
            if dom.pos <= 60 or dom.pos > 64:
                idx += 1
                continue

            it = getIcetopNum(s)

            if not stringToDom.has_key(it):
                stringToDom[it] = []
            stringToDom[it].append(dom)

            del domList[idx]

if __name__ == "__main__":
    # read in default-dom-geometry.xml
    defDomGeom = DefaultDomGeometry()

    # get the cached string->DOM map
    stringToDom = defDomGeom.getStringToDomDict()

    # rewrite the 64-DOM strings to 60 DOM strings plus 32 DOM icetop hubs
    rewrite(stringToDom)

    # dump the new default-dom-geometry data to sys.stdout
    dump(stringToDom)
