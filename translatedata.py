from anytree import RenderTree  # pip3 install anytree
from anytree.importer import DictImporter, JsonImporter
import json  # Base library
from xml.dom import minidom

from sbomify.sbomlibrary import SbomLibrary

tree = {}

with open("out.json", "r") as f:
    baseimporter = DictImporter(nodecls=SbomLibrary)
    importer = JsonImporter(dictimporter=baseimporter)
    tree = importer.read(f)

tree

#print(RenderTree(tree))
thestr = tree.toSWID()
print(thestr)
#reparsed = minidom.parseString(thestr)
#print(reparsed.toprettyxml(indent="  "))
