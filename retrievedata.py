import requests #pip3 install requests
from anytree import RenderTree #pip3 install anytree
from anytree.exporter import JsonExporter
import configparser #Base library
import json

from SBOMLibrary import SBOMLibrary, GitHubSBOMLibrary

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

    variables = {
        "ownerName": library.githubOwner,
        "repoName": library.githubRepoName
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
                tnode = GitHubSBOMLibrary(dep['node']['packageName'],
                    version = dep['node']['requirements'],
                    packageManager = dep['node']['packageManager'],
                    githubNameWithOwner = dep['node']['repository']['nameWithOwner'],
                    description = dep['node']['repository']['description'],
                    unmaintained = dep['node']['repository']['isArchived'],
                    hasDependencies = dep['node']['hasDependencies'], parentNode = library
                    )
                if dep['node']['repository']['licenseInfo'] is not None:
                    tnode.licenseString = dep['node']['repository']['licenseInfo']['spdxId']
            else:
                #print(library.packageRepositoryURL)
                print(dep)
                #exit()
                tnode = SBOMLibrary(dep['node']['packageName'],
                    version = dep['node']['requirements'],
                    packageManager = dep['node']['packageManager'],
                    #githubNameWithOwner = dep['node']['repository']['nameWithOwner'],
                    hasDependencies = False, incompleteReason = "Unable to determine repository host",
                    parent = library # TODO THIS IS WRONG
                    )

foom = GitHubSBOMLibrary("snipe-it", githubNameWithOwner = "snipe/snipe-it", hasDependencies = True)
retrieveDependencies(foom)
for child in foom.children:
   retrieveDependencies(child)

with open("out.json", "w") as f:
    exporter = JsonExporter(indent=2, sort_keys=True)
    exporter.write(foom, f)
