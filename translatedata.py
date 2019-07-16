from anytree import RenderTree #pip3 install anytree
from anytree.importer import JsonImporter
import configparser #Base library
import json # Base library

from SBOMLibrary import SBOMLibrary, GitHubSBOMLibrary

tree = {}

with open("out.json", "r") as f:
    importer = JsonImporter()
    tree = importer.read(f)

print(RenderTree(tree))

#
