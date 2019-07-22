from anytree import NodeMixin
from xml.etree.ElementTree import Element, SubElement, tostring


class SbomLibrary(NodeMixin):
    def __init__(
            self, name,
            description=None,
            hasDependencies=False,
            incompleteReason=None,
            licenseString=None,
            packageManager=None,
            packageRepositoryURL=None,
            unmaintained=False,
            version=None,
            parent=None,
            children=None):

        self.description = description
        self.hasDependencies = hasDependencies
        self.incompleteReason = incompleteReason
        self.licenseString = licenseString

        self.name = name
        self.packageManager = packageManager
        self.packageRepositoryURL = packageRepositoryURL
        self.unmaintained = unmaintained
        self.version = version

        self.parent = parent
        if children:
            self.children = children

    def makeCycloneDXRepresentationOfNode(self):

        component = Element('component')
        component.set("type", "library")
        name = SubElement(component, "name")
        name.text = self.name
        version = SubElement(component, "version")
        version.text = self.version  # TODO: This isn't really correct
        description = SubElement(component, "description")
        description.text = self.description
        outerlicense = SubElement(component, "licenses")
        license = SubElement(outerlicense, "license")
        licensename = SubElement(license, "name")
        licensename.text = self.licenseString
        packageURL = SubElement(component, "purl")
        packageURL.text = self.packageRepositoryURL

        if len(self.children) > 0:
            components = SubElement(component, "components")
            for child in self.children:
                childxml = child.makeCycloneDXRepresentationOfNode()
                components.append(childxml)

        return component

    def toCycloneDX(self):

        components = self.makeCycloneDXRepresentationOfNode()

        bom = Element("bom")
        bom.set("version", "1")
        bom.set("xmlns", "http://cyclonedx.org/schema/bom/1.0")
        componentsholder = SubElement(bom, "components")
        componentsholder.append(components)

        return tostring(bom)

    def sbomToSPDX(sbomRoot):
        return "TODO SPDX output"

    def sbomToSWID(sbomRoot):
        return "TODO SWID output"

    def sbomToJSON(sbomRoot):
        return "TODO JSON output"

    def sbomToCoSWID(sbomRoot):
        return "TODO CoSWID output"
