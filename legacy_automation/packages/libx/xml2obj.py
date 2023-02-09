"""
=====================
xml2obj
=====================

Borrowed from wxPython XML tree demo and modified.
"""

import codecs
from xml.parsers import expat


class Element:
    """A parsed XML element"""
    def __init__(self, name, attributes):
        """Element constructor"""
        # The element's tag name
        self.name = name
        # The element's attribute dictionary
        self.attributes = attributes
        # The element's cdata
        self.cdata = ''
        # The element's child element list (sequence)
        self.children = []
        
    def AddChild(self, element):
        """Add a reference to a child element"""
        self.children.append(element)
        
    def getAttribute(self, key):
        """Get an attribute value"""
        return self.attributes.get(key)
    
    def getData(self):
        """Get the cdata"""
        return self.cdata
        
    def getElements(self, name=''):
        """Get a list of child elements"""
        #If no tag name is specified, return the all children
        if not name:
            return self.children
        else:
            # else return only those children with a matching tag name
            elements = []
            for element in self.children:
                if element.name == name:
                    elements.append(element)
            return elements


class Xml2Obj:
    """XML to Object"""
    def __init__(self):
        self.root = None
        self.nodeStack = []
        
    def StartElement(self, name, attributes):
        """SAX start element even handler"""
        # Instantiate an Element object
        element = Element(name.encode(), attributes)
        
        # Push element onto the stack and make it a child of parent
        if len(self.nodeStack) > 0:
            parent = self.nodeStack[-1]
            parent.AddChild(element)
        else:
            self.root = element
        self.nodeStack.append(element)
        
    def EndElement(self, name):
        """SAX end element event handler"""
        self.nodeStack = self.nodeStack[:-1]

    def CharacterData(self, data):
        """SAX character data event handler"""
        if data.strip():
            element = self.nodeStack[-1]
            element.cdata += data
            return

    def Parse(self, filename):
        # Create a SAX parser
        parser = expat.ParserCreate()

        # SAX event handlers
        parser.StartElementHandler = self.StartElement
        parser.EndElementHandler = self.EndElement
        parser.CharacterDataHandler = self.CharacterData

        # Parse the XML File
        lines = codecs.open(filename, 'r', encoding='utf-8').read()
        ParserStatus = parser.Parse(lines, 1)

        return self.root
    

