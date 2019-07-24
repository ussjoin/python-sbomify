import requests  # pip3 install requests
from anytree.exporter import JsonExporter
import configparser  # Base library
import json

from sbomify.sbomlibrary import SbomLibrary

config = configparser.ConfigParser()
config.read('config.ini')

GITHUB_ENDPOINT = config["DEFAULT"]["GraphQLEndpoint"]
BEARER_TOKEN = config["DEFAULT"]["BearerToken"]

request_headers = {
    "Accept": "application/vnd.github.hawkgirl-preview+json",
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

def retrieveDependencies(library):
    '''Retrieves one layer of dependencies for a GitHubSBOMLibrary.'''

    if not library.hasDependencies:
        return #That was easy!

    if not library.packageRepositoryURL.startswith("https://github.com/"):
        return # TODO: Do something smarter here

    ownerandrepo = library.packageRepositoryURL[19:].split("/")

    if not len(ownerandrepo) >= 2:
        return # TODO: Do something smarter here

    owner = ownerandrepo[0]
    repo = ownerandrepo[1]

    variables = {
        "ownerName": owner,
        "repoName": repo
    }

    query = """
    query GetRepositoryDependencies($ownerName: String!, $repoName: String!){
      repository(owner: $ownerName, name: $repoName) {
        dependencyGraphManifests(first: 10) {
          edges {
            node {
              filename
              dependencies {
                edges {
                  node {
                    hasDependencies
                    packageManager
                    packageName
                    repository {
                      description
                      nameWithOwner
                      isArchived
                      licenseInfo {
                        spdxId
                      }
                      defaultBranchRef {
                        target {
                          oid
                        }
                      }
                    }
                    requirements
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    r = requests.post(GITHUB_ENDPOINT, headers=request_headers, json={'query': query, 'variables': variables})

    depset = r.json()['data']['repository']['dependencyGraphManifests']['edges']

    for depgroup in depset:
        deps = depgroup['node']['dependencies']['edges']
        for dep in deps:

            if dep['node']['repository'] is not None:
                tnode = SbomLibrary(dep['node']['packageName'],
                    version = dep['node']['requirements'],
                    packageManager = dep['node']['packageManager'],
                    packageRepositoryURL = f"https://github.com/{dep['node']['repository']['nameWithOwner']}",
                    unmaintained = dep['node']['repository']['isArchived'],
                    commitHash = dep['node']['repository']['defaultBranchRef']['target']['oid'],
                    description = dep['node']['repository']['description'],
                    hasDependencies = dep['node']['hasDependencies'], parent = library
                    )
                if dep['node']['repository']['licenseInfo'] is not None:
                    tnode.licenseString = dep['node']['repository']['licenseInfo']['spdxId']
            else:
                print(dep)
                tnode = SbomLibrary(dep['node']['packageName'],
                    version = dep['node']['requirements'],
                    packageManager = dep['node']['packageManager'],
                    hasDependencies = False, incompleteReason = "Unable to determine repository host",
                    parent = library
                    )

foom = SbomLibrary("snipe-it", packageRepositoryURL = "https://github.com/snipe/snipe-it", hasDependencies = True)
retrieveDependencies(foom)
# for child in foom.children:
#    retrieveDependencies(child)

with open("out.json", "w") as f:
    exporter = JsonExporter(indent=2, sort_keys=True)
    exporter.write(foom, f)
