from anytree import AnyNode

class SBOMLibrary(AnyNode): # TODO: Switch this to NodeMixin instead of just AnyNode
    def __init__(self, name, version=None, packageManager=None, packageRepositoryURL=None, hasDependencies=False, unmaintained = False, licenseString = None, incompleteReason = None, parent=None, children=None):
        #super(MyClass, self).__init__()
        self.name = name
        self.version = version
        self.packageManager = packageManager
        self.packageRepositoryURL = packageRepositoryURL
        self.hasDependencies = hasDependencies
        self.unmaintained = unmaintained
        self.licenseString = licenseString
        self.incompleteReason = incompleteReason
        self.parent = parent
        if children:
            self.children = children

class GitHubSBOMLibrary(AnyNode):
    def __init__(self, name, githubNameWithOwner, version=None, packageManager=None, hasDependencies=False, unmaintained = False, licenseString = None, description = None, incompleteReason = None, parentNode=None, children=None):
        self.githubNameWithOwner = githubNameWithOwner
        nameAndOwner = githubNameWithOwner.split("/")
        self.githubOwner = nameAndOwner[0]
        self.githubRepoName = nameAndOwner[1]
        self.name = name
        self.version = version
        self.packageManager = packageManager
        self.packageRepositoryURL = f"https://github.com/{githubNameWithOwner}"
        self.hasDependencies = hasDependencies
        self.unmaintained = unmaintained
        self.description = description
        self.licenseString = licenseString
        self.incompleteReason = incompleteReason
        self.parent = parentNode
        if children:
            self.children = children
