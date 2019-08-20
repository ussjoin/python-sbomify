from anytree import NodeMixin
from xml.etree.ElementTree import Element, SubElement, tostring


class SbomLibrary(NodeMixin):
    def __init__(
            self, name,
            commitHash=None,
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

        self.commitHash = commitHash
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

    def makeSPDXTagId(self):
        # SPDX tags seem to be internally valid only, rather than needing to be global.
        return f"SPDXRef-{self.name}-{self.commitHash}"

    def makeSPDXRepresentationOfNode(self):
        representation = (
            f"PackageName: {self.name} \n"
            f"SPDXID: {self.makeSPDXTagId()} \n"
            f"PackageVersion: {self.version} \n" # TODO: not really correct
            f"PackageDownloadLocation: {self.packageRepositoryURL} \n"
            f"PackageHomePage: {self.packageRepositoryURL} \n"
            f"PackageLicenseDeclared: {self.licenseString} \n"
        )

        # Make the forward links
        for child in self.children:
            link = f"Relationship: {self.makeSPDXTagId()} HAS_PREREQUISITE {child.makeSPDXTagId()}"
            representation += f"\n{link}"

        # Now go do the kids.
        for child in self.children:
            representation += "\n" + child.makeSPDXRepresentationOfNode()

        return representation

    def toSPDX(self):

        rep = self.makeSPDXRepresentationOfNode()
        return rep

    def makeSWIDTagId(self):
        # TODO: Resolve inherent issue that https://nvlpubs.nist.gov/nistpubs/ir/2016/NIST.IR.8060.pdf
        # (specifcally 4.5.2 on p.37) points out that tag IDs can only be valid IFF they're maintained in
        # one place, by the software creator, which means that for open metadata-derived tags they're probably
        # not good enough.
        # Anyway, given that, let's just make up a tag.
        # For now, it's name-commitHash, which will at least say very distinctly what it is.
        return f"{self.name}-{self.commitHash}"

    def makeSWIDRepresentationOfNode(self):
        component = Element('SoftwareIdentity')
        component.set("name", self.name)
        if self.version:
            component.set("version", self.version)  # TODO: This isn't really correct for version....
        component.set("versionScheme", "alphanumeric")
        component.set("xmlns", "http://standards.iso.org/iso/19770/-2/2015/schema.xsd")
        component.set("xmlns:n8060", "http://csrc.nist.gov/schema/swid/2015-extensions/swid-2015-extensions-1.0.xsd")

        tagId = self.makeSWIDTagId()
        component.set("tagId", tagId)

        entity = SubElement(component, "Entity")
        entity.set("name", "TODO: What name goes here?")
        entity.set("regid", "TODO: What?")
        entity.set("role", "tagCreator")

        # Make the forward links
        for child in self.children:
            link = SubElement(component, "Link")
            link.set("rel", "requires")
            link.set("href", f"swid:{child.makeSWIDTagId()}")

        # Now, go fetch the full tags and append them
        returnables = [{"tagId": tagId, "tag": component}]
        for child in self.children:
            returnables.extend(child.makeSWIDRepresentationOfNode())

        return returnables

    def toSWID(self):
        # Documentation: https://nvlpubs.nist.gov/nistpubs/ir/2016/NIST.IR.8060.pdf
        # SWID theory of operation
        #
        # SWID doesn't allow nesting of component tags. However, it does allow a
        # link tag that points to another SWID tag. Using this, we'll return
        # what's basically a flattening of the dependency tree, where each tag
        # contains pointers to its dependencies, but not the full tag of the
        # dependency.

        arr = self.makeSWIDRepresentationOfNode()
        # arr is now an array of dicts, with keys tagId and tag. The latter is XMLable.
        print(arr)
        for item in arr:
            item["tag"] = tostring(item["tag"])

        # So what should happen at this point:
        # 1) Caller makes a directory called swidtag
        # 2) Caller writes each tag to a file named "<tagid>.swidtag" in that folder
        # But doing those are outside the scope of this method.
        return arr

    def sbomToJSON(sbomRoot):
        return "TODO JSON output"
